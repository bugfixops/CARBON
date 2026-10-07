"""Gemini (Vertex AI) chat client shared by the AdbGPT and ReActDroid adapters.

Both tools build OpenAI-style message lists. This module sends those lists to
Gemini unchanged, so each tool keeps its own prompts, history handling and
temperature. Messages are converted the same way CARBON's
carbon/my_gpt.py::_generate_vertex converts them (a system turn becomes a
"[System]: ..." user turn followed by an "Understood." model turn), so every
tool in the comparison talks to the model through the same interface.

Every call is appended to BASELINE_USAGE_FILE as one JSON line, including
thinking tokens. Vertex bills thinking at the output rate; CARBON's own cost
log only counted candidatesTokenCount, so this file is the one to use for cost.

Configuration (environment, or the CARBON repo's .env):
    LLM_PROVIDER    vertex (API key, default) or vertex-adc (service account)
    LLM_API_KEY     Vertex API key, for LLM_PROVIDER=vertex
    GCP_PROJECT_ID  for vertex-adc (else read from GOOGLE_APPLICATION_CREDENTIALS)
    VERTEX_LOCATION default us-central1; "global" uses the global endpoint,
                    which spreads Gemini requests across regions
    BASELINE_MODEL  default gemini-2.5-pro (falls back to LLM_MODEL)
    BASELINE_USAGE_FILE  JSONL path the harness sets for each run
    BASELINE_STOP_FILE   if this file exists, further calls are refused
"""
import json
import os
import time
from pathlib import Path

import requests

# USD per 1M tokens. Vertex AI list prices for gemini-2.5-pro: prompts up to
# 200k tokens bill at the lower rate, longer prompts at the higher rate.
# Output includes thinking tokens.
PRICES = {
    "gemini-2.5-pro": {"in": 1.25, "out": 10.00, "in_long": 2.50, "out_long": 15.00,
                       "long_threshold": 200_000},
}

_REPO_ROOT = Path(__file__).resolve().parents[2]
_adc_creds = None


class LLMRefused(RuntimeError):
    """Raised when the harness has asked the run to stop calling the model."""


def _load_dotenv():
    """Read KEY=VALUE pairs from the CARBON repo's .env without overriding the
    environment. Kept dependency-free so both tool venvs can import it."""
    env_file = _REPO_ROOT / ".env"
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


def model_name():
    return os.environ.get("BASELINE_MODEL") or os.environ.get("LLM_MODEL") or "gemini-2.5-pro"


def call_cost(model, prompt_tokens, output_tokens):
    """Cost in USD of one call; output_tokens must include thinking tokens."""
    p = PRICES.get(model)
    if p is None:
        return None
    long_prompt = prompt_tokens > p["long_threshold"]
    rate_in = p["in_long"] if long_prompt else p["in"]
    rate_out = p["out_long"] if long_prompt else p["out"]
    return prompt_tokens / 1e6 * rate_in + output_tokens / 1e6 * rate_out


def _adc_token():
    global _adc_creds
    import google.auth
    from google.auth.transport.requests import Request
    if _adc_creds is None or not _adc_creds.valid:
        _adc_creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _adc_creds.valid:
        _adc_creds.refresh(Request())
    return _adc_creds.token


def _adc_project():
    project = os.environ.get("GCP_PROJECT_ID", "")
    if not project:
        sa_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        try:
            project = json.loads(Path(sa_file).read_text()).get("project_id", "")
        except Exception:
            project = ""
    if not project:
        raise RuntimeError("vertex-adc needs GCP_PROJECT_ID or GOOGLE_APPLICATION_CREDENTIALS")
    return project


def _host(location):
    # The global endpoint has no region prefix in its host name.
    return "aiplatform.googleapis.com" if location == "global" else f"{location}-aiplatform.googleapis.com"


def _endpoint(model):
    """URL and headers, built the same way as CARBON's my_gpt._generate_vertex."""
    provider = os.environ.get("LLM_PROVIDER", "vertex").lower()
    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    if provider == "vertex-adc":
        url = (f"https://{_host(location)}/v1/projects/{_adc_project()}"
               f"/locations/{location}/publishers/google/models/{model}:generateContent")
        return url, {"Authorization": f"Bearer {_adc_token()}"}
    if provider != "vertex":
        raise RuntimeError(f"LLM_PROVIDER={provider!r} is not supported here; use vertex or vertex-adc")
    key = os.environ.get("LLM_API_KEY", "")
    if not key:
        raise RuntimeError("LLM_API_KEY is not set (CARBON .env or environment)")
    url = (f"https://{_host(location)}/v1/publishers/google/models/"
           f"{model}:generateContent?key={key}")
    return url, {}


def to_contents(messages):
    """OpenAI-style messages -> Vertex contents, identical to CARBON's conversion."""
    contents = []
    for msg in messages:
        role, content = msg["role"], msg["content"]
        if role == "system":
            contents.append({"role": "user", "parts": [{"text": f"[System]: {content}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": content}]})
        else:
            contents.append({"role": "user", "parts": [{"text": content}]})
    return contents


def _record(entry):
    path = os.environ.get("BASELINE_USAGE_FILE")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def chat(messages, temperature, tag, max_attempts=10, request_timeout=170):
    """Send one chat turn and return the reply text.

    Retries rate limits (429), server errors and network timeouts with backoff,
    for up to about 20 minutes, then raises. Each wait is logged as
    "backoff_s"; the harness adds that time back to the run's budget, so a
    quota wait does not shorten the tool's 30 minutes. A call that still fails
    is logged with "final": true and the harness marks the run llm_error
    (an infrastructure failure to re-run, not a tool result). Callers keep
    their own upstream error handling.
    """
    stop_file = os.environ.get("BASELINE_STOP_FILE")
    if stop_file and os.path.exists(stop_file):
        raise LLMRefused(Path(stop_file).read_text(encoding="utf-8", errors="replace").strip())

    model = model_name()
    payload = {"contents": to_contents(messages),
               "generationConfig": {"temperature": temperature}}
    last_error = None
    for attempt in range(1, max_attempts + 1):
        url, headers = _endpoint(model)
        started = time.time()
        try:
            resp = requests.post(url, json=payload, headers=headers or None, timeout=request_timeout)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise requests.HTTPError(f"HTTP {resp.status_code}: {resp.text[:300]}", response=resp)
            resp.raise_for_status()
            data = resp.json()
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            last_error = e
            status = getattr(getattr(e, "response", None), "status_code", None)
            final = attempt == max_attempts or (status is not None and status < 500 and status != 429)
            wait = 0 if final else min(15 * 2 ** (attempt - 1), 180)
            _record({"ts": time.time(), "tag": tag, "model": model, "ok": False, "final": final,
                     "attempt": attempt, "status": status, "backoff_s": wait, "error": str(e)[:300]})
            if final:
                break
            time.sleep(wait)
            continue

        latency = time.time() - started
        usage = data.get("usageMetadata", {}) or {}
        prompt_tokens = usage.get("promptTokenCount", 0) or 0
        visible = usage.get("candidatesTokenCount", 0) or 0
        thoughts = usage.get("thoughtsTokenCount", 0) or 0
        candidates = data.get("candidates") or []
        parts = (candidates[0].get("content", {}) or {}).get("parts", []) if candidates else []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        finish = candidates[0].get("finishReason") if candidates else None
        _record({"ts": time.time(), "tag": tag, "model": model, "ok": True, "attempt": attempt,
                 "latency_s": round(latency, 2), "prompt_tokens": prompt_tokens,
                 "output_tokens": visible, "thought_tokens": thoughts,
                 "cost_usd": call_cost(model, prompt_tokens, visible + thoughts),
                 "finish_reason": finish, "empty_reply": text == ""})
        return text
    raise RuntimeError(f"Gemini call failed after {max_attempts} attempts: {last_error}")


def usage_totals(path):
    """Sum a BASELINE_USAGE_FILE: successful calls, tokens and cost."""
    totals = {"calls": 0, "failed_attempts": 0, "failed_calls": 0, "backoff_s": 0,
              "prompt_tokens": 0, "output_tokens": 0, "thought_tokens": 0, "cost_usd": 0.0}
    if not path or not os.path.exists(path):
        return totals
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if not e.get("ok"):
                totals["failed_attempts"] += 1
                totals["failed_calls"] += 1 if e.get("final") else 0
                totals["backoff_s"] += e.get("backoff_s", 0) or 0
                continue
            totals["calls"] += 1
            totals["prompt_tokens"] += e.get("prompt_tokens", 0)
            totals["output_tokens"] += e.get("output_tokens", 0)
            totals["thought_tokens"] += e.get("thought_tokens", 0)
            totals["cost_usd"] += e.get("cost_usd") or 0.0
    totals["cost_usd"] = round(totals["cost_usd"], 4)
    return totals


if __name__ == "__main__":
    # Smoke test: one tiny call (about $0.001). Used by preflight.py --llm.
    reply = chat([{"role": "user", "content": "Reply with the single word OK."}],
                 temperature=0, tag="preflight")
    print(json.dumps({"model": model_name(), "reply": reply.strip()[:40]}))
