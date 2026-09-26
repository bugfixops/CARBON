"""
Validate a Groq model id against the account's model list (smoke-test gate).

    python validate_groq.py --model meta-llama/llama-3.2-90b-vision-preview

Reads the key from GROQ_API_KEY_1 (or LLM_API_KEY). Exits 0 when the model is
available, 2 with a clear message (including a fallback suggestion) when it is
not. Never prints key material.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
FALLBACK = "llama-3.2-11b-vision-preview"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    args = p.parse_args()
    key = os.environ.get("GROQ_API_KEY_1", "") or os.environ.get("LLM_API_KEY", "")
    if not key:
        sys.exit("[validate_groq] FATAL: set GROQ_API_KEY_1 (or LLM_API_KEY).")
    req = urllib.request.Request(
        GROQ_MODELS_URL,
        headers={"Authorization": f"Bearer {key}", "User-Agent": "rebl-retest"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("[validate_groq] FATAL: key rejected (401). Check GROQ_API_KEY_1.")
        sys.exit(f"[validate_groq] FATAL: Groq /models -> HTTP {e.code}.")
    except Exception as e:
        sys.exit(f"[validate_groq] FATAL: cannot reach Groq /models: {e}")
    ids = {m.get("id") for m in data.get("data", [])}
    print(f"[validate_groq] {len(ids)} model(s) visible on this account.")
    for i in sorted(ids):
        print(f"[validate_groq]   - {i}")
    if args.model in ids:
        print(f"[validate_groq] OK: '{args.model}' is available.")
        return
    sugg = (f" Re-run with --model {FALLBACK} (available on this account)."
            if FALLBACK in ids else "")
    vision = sorted(i for i in ids if "vision" in i.lower())
    sys.exit(f"[validate_groq] FATAL: model '{args.model}' NOT available on this "
             f"Groq account.{sugg} Vision-capable models: {vision or 'none visible'}")


if __name__ == "__main__":
    main()
