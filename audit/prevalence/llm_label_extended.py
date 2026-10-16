"""Fourth rubric: an extended labelling pass over the 3,500 sampled reports, for six
gestures that the first rubric (llm_label.py) had no category for: fling, shake,
drawing, edge swipe, one-finger zoom and two-finger rotate.

Same question as the first rubric: which of these actions must the reporter perform
to TRIGGER the bug (or to reach the state where it shows)? A gesture counts only
if the report states or clearly implies it, and every label comes with a quote.
These labels were not checked by the authors.

Gemini 3.8 Flash on Vertex AI (global endpoint), temperature 0, JSON output, one
call per report; results are cached, so a re-run only labels new reports.

  python llm_label_extended.py            # all 3,500 -> labels_sample3500_extended.jsonl
  python llm_label_extended.py --limit 20 # a pilot
"""
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import google.auth
import requests
from google.auth.transport.requests import Request

HERE = Path(__file__).resolve().parent
OUT = HERE / "labels_sample3500_extended.jsonl"
MODEL = "gemini-3.8-flash"
PRICE_IN, PRICE_OUT = 0.75, 3.75  # USD per 1M tokens (output includes thinking)

RUBRIC = """You label Android bug reports by the gesture needed to trigger the bug.

Decide whether reproducing the bug requires one of these specific gestures, performed
on the touch screen or with the device. Count a gesture only if the report states or
clearly implies that it triggers the bug or is needed to reach the state where the bug
shows; the report may describe it in plain words without naming it.

- fling: a fast swipe that leaves content moving (flinging a list, carousel or page);
  a normal slow scroll or swipe does NOT count.
- shake: physically shaking the device (shake-to-undo, shake-to-silence, shake gesture).
- drawing: drawing or writing with a finger or stylus along a path (strokes on a canvas,
  whiteboard, signature pad, handwriting, unlock pattern).
- edge_swipe: a swipe starting at the screen edge, including the system back gesture,
  predictive back, or gesture navigation (swipe up from the bottom edge to go home).
- one_finger_zoom: double-tap and then drag up or down without lifting, to zoom.
- two_finger_rotate: two fingers turning around each other to rotate a map, image or view.
- none: none of these is needed (taps, typing, ordinary scrolls or swipes, pinches,
  drags, long presses and device rotation are labelled elsewhere and count as none here).

Reply with JSON only: {"label": "<one label>", "evidence": "<a short quote from the report>", "confidence": <0 to 1>}"""
LABELS = {"fling", "shake", "drawing", "edge_swipe", "one_finger_zoom", "two_finger_rotate", "none"}

_lock = threading.Lock()
_creds = None


def token():
    global _creds
    with _lock:
        if _creds is None:
            _creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        if not _creds.valid:
            _creds.refresh(Request())
        return _creds.token


def project():
    p = os.environ.get("GCP_PROJECT_ID")
    if not p:
        for line in open(HERE.parent / ".env"):
            if line.startswith("GCP_PROJECT_ID="):
                p = line.split("=", 1)[1].strip().strip('"\'')
    return p


def call(title, body, proj):
    url = (f"https://aiplatform.googleapis.com/v1/projects/{proj}/locations/global/"
           f"publishers/google/models/{MODEL}:generateContent")
    payload = {"contents": [{"role": "user", "parts": [{"text": f"{RUBRIC}\n\n--- BUG REPORT ---\nTitle: {title}\n\n{body[:12000]}"}]}],
               "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    for attempt in range(8):
        r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token()}"}, timeout=120)
        if r.status_code == 200:
            d = r.json()
            return json.loads(d["candidates"][0]["content"]["parts"][0]["text"]), d.get("usageMetadata", {})
        if r.status_code in (429, 500, 503):
            time.sleep(min(10 * 2 ** attempt, 120))
            continue
        raise RuntimeError(f"{r.status_code} {r.text[:200]}")
    raise RuntimeError("gave up after retries")


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    done = {json.loads(l)["url"] for l in open(OUT)} if OUT.exists() else set()
    todo = [json.loads(l) for l in open(HERE / "raw_sample3500.jsonl")]
    todo = [r for r in todo if r["url"] not in done][:limit]
    proj = project()
    token()
    cost, lock = 0.0, threading.Lock()

    def work(rec):
        res, um = call(rec.get("title") or "", rec.get("body") or "", proj)
        label = str(res.get("label", "")).strip().lower()
        if label not in LABELS:
            label = "none"
        out = um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)
        c = (um.get("promptTokenCount", 0) * PRICE_IN + out * PRICE_OUT) / 1e6
        return {"url": rec["url"], "ext_label": label, "ext_evidence": res.get("evidence", ""),
                "ext_confidence": res.get("confidence"), "model": MODEL, "cost_usd": round(c, 6)}

    with open(OUT, "a") as f, ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(work, r) for r in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                row = fut.result()
            except Exception as e:
                print("error:", e, file=sys.stderr)
                continue
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                cost += row["cost_usd"]
            if i % 250 == 0:
                print(f"{i}/{len(todo)} labelled, ${cost:.2f}", flush=True)
    print(f"done: {len(todo)} reports this run, ${cost:.2f}")


if __name__ == "__main__":
    main()
