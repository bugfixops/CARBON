"""
Validate the Vertex AI ADC setup (smoke-test gate for carbon-retest-gemini).

Checks, in order:
  1. GOOGLE_APPLICATION_CREDENTIALS points to a readable service-account JSON.
  2. An OAuth2 access token can be minted via google-auth (no API call yet).
  3. Vertex AI generateContent answers on the requested model -- catches a
     disabled Vertex AI API (403), a wrong model id / region (404), and
     quota problems (429).

Usage:
    GOOGLE_APPLICATION_CREDENTIALS=/path/sa.json python validate_gemini.py --model gemini-2.5-pro

Never prints credential material.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def _fail(msg):
    sys.exit(f"[validate_gemini] FATAL: {msg}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-2.5-pro"),
                   help="Vertex AI model id (default: gemini-2.5-pro)")
    args = p.parse_args()

    sa_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not sa_file or not os.path.isfile(sa_file):
        _fail("GOOGLE_APPLICATION_CREDENTIALS is not set to an existing file. "
              "The workflow writes it from the GCP_SA_JSON secret.")
    try:
        with open(sa_file, encoding="utf-8") as f:
            sa = json.load(f)
    except Exception as e:
        _fail(f"cannot parse service-account JSON: {e}")
    project = os.environ.get("GCP_PROJECT_ID", "") or sa.get("project_id", "")
    if not project:
        _fail("no project_id found: set GCP_PROJECT_ID or use a service-account "
              "JSON that contains project_id.")
    print(f"[validate_gemini] project={project}")

    try:
        import google.auth
        from google.auth.transport.requests import Request as GARequest
    except ImportError:
        _fail("the 'google-auth' package is not installed "
              f"(interpreter: {sys.executable}). Install it with: "
              "python -m pip install google-auth")
    try:
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(GARequest())
        token = creds.token
    except Exception as e:
        _fail(f"could not mint ADC access token: {e}")
    print("[validate_gemini] ADC token minted OK.")

    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    url = (f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}"
           f"/locations/{location}/publishers/google/models/{args.model}:generateContent")
    payload = {"contents": [{"role": "user", "parts": [{"text": "Reply with exactly: OK"}]}],
               # pro is a thinking model: give it room for thought tokens + the reply
               "generationConfig": {"temperature": 0.0, "maxOutputTokens": 64}}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": "rebl-retest"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        if e.code == 403:
            _fail(f"HTTP 403 from Vertex AI: enable the Vertex AI API on project "
                  f"'{project}' and grant the service account roles/aiplatform.user. "
                  f"Detail: {body}")
        if e.code == 404:
            _fail(f"HTTP 404: model '{args.model}' not found in {location}. Detail: {body}")
        _fail(f"Vertex AI generateContent -> HTTP {e.code}. Detail: {body}")
    except Exception as e:
        _fail(f"cannot reach Vertex AI: {e}")
    # The gate checks reachability + auth, not the exact reply wording: pro may
    # spend its budget on thought tokens (finishReason MAX_TOKENS) without
    # emitting a text part. Any non-empty candidates list on HTTP 200 is a pass.
    try:
        cand = data["candidates"][0]
    except Exception:
        _fail(f"unexpected Vertex AI response shape: {str(data)[:300]}")
    finish = cand.get("finishReason", "?")
    text = ""
    try:
        for part in cand.get("content", {}).get("parts", []):
            if isinstance(part, dict) and part.get("text"):
                text = part["text"].strip()
                break
    except Exception:
        pass
    um = data.get("usageMetadata", {})
    print(f"[validate_gemini] OK: model '{args.model}' reachable via Vertex AI "
          f"(finishReason={finish}, prompt_tokens={um.get('promptTokenCount')}, "
          f"total_tokens={um.get('totalTokenCount')}): {text!r}"
          + ("" if text else " [no text part emitted]"))


if __name__ == "__main__":
    main()
