"""
Multi-provider LLM client for ReBL.
Reads LLM_PROVIDER, LLM_API_KEY, LLM_MODEL from .env via llm_config.py.
Supports: Gemini, OpenAI, Groq, Ollama, or any OpenAI-compatible endpoint.

Multi-account failover (carbon-retest-groq):
  generate_text() classifies API failures per key:
    * 401 / auth errors  -> key marked PERMANENTLY exhausted, rotate, retry now
    * 429 (rate limit)   -> honor Retry-After, key exhausted for the day, rotate
    * 5xx               -> key exhausted for the day, rotate
  Rotation rebuilds the HTTP client so the NEW key is actually used
  (previously _client kept the old key after rotation).
"""

import datetime
import math
import time
import json
import os
from utils import *
from llm_config import get_config, rotate_key, get_current_key_info, mark_key_exhausted, keys_remaining

# Load LLM config
LLM = get_config()
print(f"[LLM] Provider: {LLM['provider']} | Model: {LLM['model']} | Vision: {LLM['supports_vision']}")
print(f"[LLM] Using {get_current_key_info()}")


def _make_openai_client(api_key, base_url):
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base_url)


# ── Provider-specific setup ──────────────────────────────────────────────────

if LLM['type'] == 'gemini':
    import google.generativeai as genai
    genai.configure(api_key=LLM['api_key'])
elif LLM['type'] == 'openai':
    _client = _make_openai_client(LLM['api_key'], LLM.get('base_url'))
elif LLM['type'] == 'vertex':
    import requests as _requests


def _refresh_client():
    """Rebuild the OpenAI-compatible client from the CURRENT key.

    Must be called after every rotate_key(): the client created at import
    time otherwise keeps sending the OLD (dead) key."""
    global _client
    if LLM.get('type') == 'openai':
        _client = _make_openai_client(LLM['api_key'], LLM.get('base_url'))
        print(f"[LLM] Client rebuilt with {get_current_key_info()}")


# Check if vision/screenshot support is available
try:
    from ui_viewer import is_vision_available
    VISION_ENABLED = is_vision_available() and LLM['supports_vision']
except ImportError:
    VISION_ENABLED = False


# ── Token usage / cost tracking ──────────────────────────────────────────────
# Accumulates per-process (one process == one reproduction case) so each case's
# log can report exactly how many tokens (and $) it consumed.

TOKEN_USAGE = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

# USD per 1M tokens. Extend as needed for other models.
# Groq free-tier models cost $0.00.
_PRICING_PER_1M = {
    "gpt-4o":       {"in": 2.50, "out": 10.00},
    "gpt-4o-mini":  {"in": 0.15, "out": 0.60},
    "gpt-4.1":      {"in": 2.00, "out": 8.00},
    "llama-3.2":    {"in": 0.00, "out": 0.00},
    "llama-3.3":    {"in": 0.00, "out": 0.00},
    "meta-llama/":  {"in": 0.00, "out": 0.00},
    # Vertex AI list prices (Sep 2026) -- bills the GCP billing account / trial credit.
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50},
    "gemini-2.5-pro":   {"in": 1.25, "out": 10.00},
}


def record_usage(usage):
    """Add one API call's token usage to the running total, and flush a sidecar
    file so the total survives even if the process is killed mid-run (timeouts)."""
    if not usage:
        return
    TOKEN_USAGE["calls"] += 1
    TOKEN_USAGE["prompt_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
    TOKEN_USAGE["completion_tokens"] += getattr(usage, "completion_tokens", 0) or 0
    TOKEN_USAGE["total_tokens"] += getattr(usage, "total_tokens", 0) or 0
    # Flush running total to a sidecar file (path from env), so run_dataset can
    # read it even for timed-out cases that never reach the end-of-case print.
    sidecar = os.environ.get("REBL_TOKEN_FILE")
    if sidecar:
        try:
            cost = estimate_cost(LLM['model'])
            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump({**TOKEN_USAGE, "model": LLM['model'], "est_cost_usd": cost}, f)
        except Exception:
            pass


def estimate_cost(model_name):
    """Estimate USD cost of accumulated tokens for the given model (best-effort)."""
    key = None
    for k in _PRICING_PER_1M:
        if model_name and model_name.startswith(k):
            key = k
            break
    if key is None:
        return None
    p = _PRICING_PER_1M[key]
    cost = (TOKEN_USAGE["prompt_tokens"] / 1_000_000.0) * p["in"] \
         + (TOKEN_USAGE["completion_tokens"] / 1_000_000.0) * p["out"]
    return round(cost, 4)


def token_usage_report(model_name):
    """Human-readable one-block token+cost summary for the current case."""
    cost = estimate_cost(model_name)
    cost_str = f"${cost}" if cost is not None else "n/a (unknown model pricing)"
    return (
        "\n===== TOKEN USAGE (this case) =====\n"
        f"  API calls:         {TOKEN_USAGE['calls']}\n"
        f"  Prompt tokens:     {TOKEN_USAGE['prompt_tokens']}\n"
        f"  Completion tokens: {TOKEN_USAGE['completion_tokens']}\n"
        f"  Total tokens:      {TOKEN_USAGE['total_tokens']}\n"
        f"  Est. cost ({model_name}): {cost_str}\n"
        "==================================="
    )


# ── Token counting ───────────────────────────────────────────────────────────

def count_tokens(message):
    return len(message) // 4

def count_chat_history_tokens(chat_history):
    total = 0
    for msg in chat_history:
        total += count_tokens(msg['content'])
        total += count_tokens(msg['role'])
    return total

def truncate_message(message, n):
    estimated = len(message) // 4
    if estimated <= n:
        return False, None
    char_limit = math.floor(n * 4)
    return True, message[:char_limit]


# ── History management ───────────────────────────────────────────────────────

def convert_history_to_text(history):
    text = ""
    for msg in history:
        role = msg['role']
        content = msg['content']
        if role == 'system':
            text += f"System: {content}\n\n"
        elif role == 'user':
            text += f"User: {content}\n\n"
        elif role == 'assistant':
            text += f"Assistant: {content}\n\n"
    return text

def _summarize(history):
    """Summarize history when it gets too long."""
    summary_prompt = ('The conversation is about to exceed the limit, before we '
                      'continue the reproduction process. Can you summarize the '
                      'above conversation. Note that You shouldn\'t summarize the '
                      'rule and keep the rules as original since the rules are the standards.')
    history.append({"role": "user", "content": summary_prompt})

    if LLM['type'] == 'gemini':
        model = genai.GenerativeModel(f"models/{LLM['model']}")
        response = model.generate_content(convert_history_to_text(history))
        return response.text
    elif LLM['type'] == 'vertex':
        result, _ = _generate_vertex(history, LLM['model'], None)
        return result["choices"][0]["message"]["content"]
    else:
        response = _client.chat.completions.create(
            model=LLM['model'],
            messages=history,
            temperature=0.3,
        )
        return response.choices[0].message.content


# The seed training prompts are a fixed 21-message few-shot preamble
# (1 system + 10 user/assistant pairs). Index 21 is the bug report. Everything
# after that is the growing per-step conversation loop.
SEED_PROMPT_COUNT = 21

# Sliding-window cap: keep at most this many of the MOST RECENT loop messages
# (user prompt + assistant reply per step). Older steps are dropped. Without
# this, every step re-sends the entire (verbose UI-hierarchy) history, which on
# gpt-4o ballooned to 2-5M tokens / $5-12 for a single long case.
MAX_RECENT_LOOP_MESSAGES = int(os.environ.get("REBL_HISTORY_WINDOW", "12"))


def _trim_history(history):
    """Keep seed prompts + bug report + the last MAX_RECENT_LOOP_MESSAGES turns.
    Drops the oldest loop messages so per-call token size stays bounded."""
    if len(history) <= SEED_PROMPT_COUNT + 1 + MAX_RECENT_LOOP_MESSAGES:
        return history
    head = history[:SEED_PROMPT_COUNT + 1]          # seed + bug report
    tail = history[-MAX_RECENT_LOOP_MESSAGES:]       # most recent turns
    # Insert a short marker so the model knows earlier steps were elided.
    marker = {"role": "user",
              "content": "[Earlier exploration steps omitted to conserve context. "
                         "Continue based on the current screen and recent steps.]"}
    return head + [marker] + tail


def process_history(prompt, history, max_tokens, threshold):
    # Append the new prompt, then apply the sliding-window trim. This bounds the
    # size of every outgoing request regardless of how many steps a case takes.
    history.append({"role": "user", "content": prompt})
    history = _trim_history(history)
    return history


class _PromptTooLargeError(RuntimeError):
    """Raised when the prompt alone exceeds the provider's per-request TPM cap.

    Retrying can never fix this (the request is oversized by construction);
    generate_text() must fail fast instead of burning the attempt budget."""


# ── Failure classification for multi-account failover ────────────────────────

def _http_status(e):
    for attr in ("status_code",):
        v = getattr(e, attr, None)
        if isinstance(v, int):
            return v
    resp = getattr(e, "response", None)
    if resp is not None:
        v = getattr(resp, "status_code", None)
        if isinstance(v, int):
            return v
    return None


def _retry_after_seconds(e, default=20, cap=60):
    """Best-effort Retry-After extraction (seconds), bounded by cap."""
    try:
        resp = getattr(e, "response", None)
        headers = getattr(resp, "headers", None) if resp is not None else None
        if headers:
            for name in ("retry-after", "Retry-After"):
                if name in headers:
                    return max(1, min(int(float(headers[name])), cap))
        v = getattr(e, "retry_after", None)
        if v:
            return max(1, min(int(float(v)), cap))
    except Exception:
        pass
    return default


def _classify_error(e):
    """Return 'auth' | 'rate' | 'server' | 'too_large' | 'other' for an API failure."""
    status = _http_status(e)
    msg = str(e).lower()
    # 413 "request too large": the REQUEST exceeds the provider's per-request
    # token cap (Groq free tier: 8000 TPM, counts prompt_tokens + max_tokens).
    # Retrying — or rotating keys — can never fix it; the prompt/max_tokens
    # must shrink. Checked before 'rate': the message can mention rate limits.
    if status == 413 or "request too large" in msg:
        return "too_large"
    if status == 401 or "invalid_api_key" in msg or "invalid api key" in msg \
            or "unauthorized" in msg or "authentication" in msg:
        return "auth"
    if status == 429 or "429" in str(e) or "rate" in msg or "quota" in msg \
            or "resource exhausted" in msg or "too many requests" in msg:
        return "rate"
    if status is not None and 500 <= status < 600:
        return "server"
    return "other"


# ── Main generate function ───────────────────────────────────────────────────

def generate_text(prompt, history, package_name=None, model_name=None,
                  max_tokens=None, attempts=10, screenshot=None):
    model_name = model_name or LLM['model']
    max_tokens = max_tokens or LLM['max_tokens']

    history = process_history(prompt, history, max_tokens, threshold=0.75)

    last_exc = None
    for times in range(attempts):
        try:
            if LLM['type'] == 'gemini':
                return _generate_gemini(history, model_name, screenshot)
            elif LLM['type'] == 'vertex':
                return _generate_vertex(history, model_name, screenshot)
            else:
                return _generate_openai(history, model_name, screenshot)

        except Exception as e:
            last_exc = e
            if isinstance(e, _PromptTooLargeError):
                # Oversized by construction: waiting and retrying only burns
                # the case's time budget. Fail the case immediately with the
                # reason in the log.
                print(f"[LLM] {e} Failing fast (no retry).")
                if package_name:
                    save_chat_history(history, package_name)
                raise
            kind = _classify_error(e)
            print(f"Attempt {times + 1} failed [{kind}] with error: {str(e)[:300]}")

            if kind == "auth":
                # Dead account: never retry it, move on immediately.
                mark_key_exhausted(permanent=True, reason="auth failure")
                if rotate_key():
                    LLM.update(get_config())
                    _refresh_client()
                    print(f"[LLM] Rotated to {get_current_key_info()}, retrying immediately...")
                    continue
                print("[LLM] No usable keys left after auth failure.")
                raise e

            if kind == "too_large":
                # The request itself is bigger than the provider allows.
                # Retrying the same oversized request — or burning the other
                # keys on it — cannot help: fail fast with a clear message.
                raise RuntimeError(
                    "[LLM] request exceeds the provider's per-request token cap "
                    f"(TPM cap={LLM.get('tpm_limit')}). Shrink the prompt or "
                    f"max_tokens. Provider error: {str(e)[:300]}") from e

            if kind in ("rate", "server"):
                # Exhausted for the day on THIS account; keep going on the next.
                scope = "rate limit (429)" if kind == "rate" else "server error (5xx)"
                wait = _retry_after_seconds(e) if kind == "rate" else 10
                mark_key_exhausted(permanent=False, reason=scope)
                if rotate_key():
                    LLM.update(get_config())
                    _refresh_client()
                    print(f"[LLM] {scope}; backing off {wait}s then continuing "
                          f"with {get_current_key_info()}...")
                    time.sleep(wait)
                    continue
                # No keys left: wait out the rate limit, then retry same key
                # (it may recover tomorrow / after the window).
                print(f"[LLM] All keys exhausted ({keys_remaining()} usable). "
                      f"Waiting {wait}s before retry ({times + 1}/{attempts})...")
                if package_name:
                    save_chat_history(history, package_name)
                time.sleep(wait)
                continue

            # Other errors: legacy backoff behavior.
            if times < attempts - 1:
                if package_name:
                    save_chat_history(history, package_name)
                wait = 60 * (times + 1)
                print(f"Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"All {attempts} attempts failed.")
                if package_name:
                    save_chat_history(history, package_name)
                raise e

    # The rate/server branch `continue`s even on the final attempt, which used
    # to fall off the end and return None (crashing callers unpacking the
    # result). Surface the last error instead.
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("[LLM] all attempts failed with no recorded error")


def _generate_gemini(history, model_name, screenshot):
    """Generate using Google Gemini native API."""
    model = genai.GenerativeModel(f"models/{model_name}" if not model_name.startswith("models/") else model_name)
    chat_text = convert_history_to_text(history)

    content_parts = [chat_text]
    if screenshot is not None and VISION_ENABLED:
        content_parts.append(screenshot)
        print("[UIAutomator Viewer] Annotated screenshot included in prompt")

    response = model.generate_content(
        content_parts,
        generation_config=genai.types.GenerationConfig(temperature=0.3),
    )

    formatted = {
        "model": model_name,
        "choices": [{"message": {"content": response.text}}]
    }
    return formatted, history


def _generate_openai(history, model_name, screenshot):
    """Generate using OpenAI-compatible API (OpenAI, Groq, Ollama, etc.)."""
    messages = list(history)

    # Add screenshot as base64 image if vision is supported
    if screenshot is not None and VISION_ENABLED:
        import base64
        from io import BytesIO
        buf = BytesIO()
        screenshot.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Here is the current annotated screenshot:"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ]
        })
        print("[UIAutomator Viewer] Annotated screenshot included in prompt")

    # Size max_tokens so prompt_tokens + max_tokens stays under the provider's
    # TPM cap (Groq free tier: 8000). With no explicit max_tokens the provider
    # reserves its default completion budget and rejects the call with 413.
    max_tokens = LLM['max_tokens']
    extra = None
    tpm_cap = LLM.get('tpm_limit')
    if tpm_cap:
        prompt_est = 0
        for m in messages:
            c = m.get('content', '')
            if isinstance(c, str):
                prompt_est += count_tokens(c) + 4  # + role overhead
        margin = 512
        budget = tpm_cap - prompt_est - margin
        if budget < 256:
            raise _PromptTooLargeError(
                f"[LLM] prompt (~{prompt_est} tokens) already exceeds the "
                f"provider TPM cap ({tpm_cap}); no room for a completion. "
                "Shrink the prompt.")
        max_tokens = max(256, min(max_tokens, budget))
        print(f"[LLM] max_tokens={max_tokens} (prompt ~{prompt_est} tokens, TPM cap {tpm_cap})")
    if LLM.get('provider') == 'groq' and model_name.startswith('openai/gpt-oss'):
        # Reasoning tokens count toward max_tokens on gpt-oss; keep thinking
        # short so the actual answer is not truncated by the TPM-sized budget.
        extra = {"reasoning_effort": "low"}

    response = _client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3,
        max_tokens=max_tokens,
        **({"extra_body": extra} if extra else {}),
    )

    # Accumulate token usage for cost tracking (usage is returned per call).
    try:
        record_usage(response.usage)
    except Exception:
        pass

    formatted = {
        "model": response.model,
        "choices": [{"message": {"content": response.choices[0].message.content}}]
    }
    return formatted, history


# ── Vertex AI via ADC (Application Default Credentials) ──────────────────────
# For the 'vertex-adc' provider no API key exists (the account's org policy
# disallows creating them). Instead we mint a short-lived OAuth2 access token
# from the service-account file at GOOGLE_APPLICATION_CREDENTIALS and call the
# regional Vertex AI endpoint with `Authorization: Bearer <token>`.

_adc_creds = None
_adc_project = None


def _vertex_access_token():
    """OAuth2 access token from ADC, cached and refreshed as needed."""
    global _adc_creds
    try:
        import google.auth
        from google.auth.transport.requests import Request as _GARequest
    except ImportError:
        raise RuntimeError(
            "[LLM] vertex-adc needs the 'google-auth' package: pip install google-auth")
    if _adc_creds is None or not _adc_creds.valid:
        _adc_creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _adc_creds.valid:
        _adc_creds.refresh(_GARequest())
    return _adc_creds.token


def _vertex_project_id():
    """GCP project id: GCP_PROJECT_ID env, else the ADC service-account file."""
    global _adc_project
    if _adc_project:
        return _adc_project
    proj = os.environ.get("GCP_PROJECT_ID", "")
    if not proj:
        sa_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
        try:
            with open(sa_file, encoding="utf-8") as f:
                proj = json.load(f).get("project_id", "")
        except Exception:
            proj = ""
    if not proj:
        raise RuntimeError(
            "[LLM] vertex-adc needs GCP_PROJECT_ID or a service-account JSON "
            "at GOOGLE_APPLICATION_CREDENTIALS containing project_id.")
    _adc_project = proj
    return proj


def _generate_vertex(history, model_name, screenshot):
    """Generate using Vertex AI REST API — bills Google Cloud credits.
    Uses the same generateContent format as AI Studio but via aiplatform.googleapis.com.
    Supports the AQ.* API key format from Google Cloud Console.
    """
    import base64
    from io import BytesIO

    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    if LLM.get('auth') == 'adc':
        # ADC route: short-lived OAuth2 Bearer token, regional endpoint, no API key.
        project = _vertex_project_id()
        url = (f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}"
               f"/locations/{location}/publishers/google/models/{model_name}:generateContent")
        headers = {"Authorization": f"Bearer {_vertex_access_token()}"}
    else:
        base_url = LLM.get('base_url', 'https://aiplatform.googleapis.com/v1/publishers/google/models')
        if "aiplatform.googleapis.com" in base_url and "-aiplatform.googleapis.com" not in base_url:
            # The global host does not serve generateContent; use the regional endpoint.
            base_url = (f"https://{location}-aiplatform.googleapis.com/v1/"
                        f"publishers/google/models")
        url = f"{base_url}/{model_name}:generateContent?key={LLM['api_key']}"
        headers = {}

    # Build contents from history
    contents = []
    for msg in history:
        role = msg['role']
        content = msg['content']
        if role == 'system':
            # Vertex AI doesn't have system role — prepend as user turn
            contents.append({"role": "user", "parts": [{"text": f"[System]: {content}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        elif role == 'assistant':
            contents.append({"role": "model", "parts": [{"text": content}]})
        else:
            contents.append({"role": "user", "parts": [{"text": content}]})

    # Append screenshot to last user turn if available
    if screenshot is not None and VISION_ENABLED:
        buf = BytesIO()
        screenshot.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        if contents and contents[-1]['role'] == 'user':
            contents[-1]['parts'].append({
                "inline_data": {"mime_type": "image/png", "data": b64}
            })
        else:
            contents.append({"role": "user", "parts": [
                {"text": "Here is the current annotated screenshot:"},
                {"inline_data": {"mime_type": "image/png", "data": b64}},
            ]})
        print("[UIAutomator Viewer] Annotated screenshot included in prompt")

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.3},
    }

    response = _requests.post(url, json=payload, headers=headers or None, timeout=120)
    response.raise_for_status()
    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]

    # Vertex returns usageMetadata -- feed the per-case token sidecar so the
    # batch summary reports real token counts and cost (Vertex AI bills).
    try:
        from types import SimpleNamespace
        um = data.get("usageMetadata", {}) or {}
        record_usage(SimpleNamespace(
            prompt_tokens=um.get("promptTokenCount", 0),
            completion_tokens=um.get("candidatesTokenCount", 0),
            total_tokens=um.get("totalTokenCount", 0)))
    except Exception:
        pass

    formatted = {
        "model": model_name,
        "choices": [{"message": {"content": text}}]
    }
    return formatted, history


# ── Helpers ──────────────────────────────────────────────────────────────────

def save_chat_history(history, package_name):
    os.makedirs('./chat_history', exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    path = f"./chat_history/{package_name}_chat_{ts}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(history, f)

def get_model_name(response):
    return response["model"]

def get_message(response):
    return response["choices"][0]["message"]["content"]
