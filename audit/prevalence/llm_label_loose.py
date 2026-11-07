"""Third rubric: a lenient labelling pass over the 3,500 sampled reports (an upper bound).

The main pass (llm_label.py) labels the gesture that TRIGGERS the bug and needs the
report to state or clearly imply it. This pass is deliberately inclusive: it counts
a gesture whenever reproducing the bug could plausibly involve one at any step,
including setup, even when the report describes it in plain words without naming
it, and it prefers the gesture (and the most complex one) when in doubt. Its counts
are therefore an upper bound; they are not checked by hand.

Same model and settings as llm_label.py: Gemini 2.5 Flash on Vertex AI, temperature 0,
JSON output, one call per report, results cached so re-runs only label new reports.

  python llm_label_loose.py            # writes labels_sample3500_loose.jsonl
"""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import llm_label as base  # same project, token and pricing helpers

RUBRIC = """You label Android bug reports for a study of GUI gestures. Be inclusive: we
want every report where reproducing the bug could plausibly involve a gesture.

Decide which gesture, if any, a person would plausibly have to perform on the device
at ANY step while reproducing the bug, including the steps that set up the state,
even if the report does not name the gesture and describes it only in plain words
(for example "move the slider", "reorder the items", "resize the widget", "zoom the
map", "pull down the list", "flip to the next page", "go through the pages",
"tap it quickly", "before it finishes loading"). When in doubt between a gesture and
none, choose the gesture. If several gestures could be involved, give the most
complex one.

Complex or precision gestures:
- pinch_zoom: a two-finger pinch to zoom in or out.
- drag_and_drop: pressing an item or handle and dragging it to a new position.
- swipe_region: a swipe or drag that must start or end at a specific place or
  control (a seek bar or slider, the screen edge, part of a video, a map region).
- quick_tap: taps whose timing matters (rapid repeated taps, tapping during an
  animation or transition, before a timeout, while something loads).
- picker_scroll: turning a number, date or time picker wheel to a value.
- multi_touch: any other multi-finger gesture.
Common gestures and device actions:
- scroll, swipe, long_press, double_tap, orientation (rotating the device).
Otherwise:
- none: the report is not about using the app's interface at all, or taps and
  typing alone plausibly reproduce it.

Reply with JSON only: {"label": "<one label>", "evidence": "<a short quote from the
report>", "confidence": <0 to 1>}"""

LABELS = {"pinch_zoom", "drag_and_drop", "swipe_region", "quick_tap", "picker_scroll", "multi_touch",
          "scroll", "swipe", "long_press", "double_tap", "orientation", "none"}


_token_lock = threading.Lock()


def token():
    """llm_label.token() is not thread-safe; serialise the refresh."""
    with _token_lock:
        return base.token()


def call(title, body, proj):
    url = (f"https://us-central1-aiplatform.googleapis.com/v1/projects/{proj}/locations/us-central1/"
           f"publishers/google/models/{base.MODEL}:generateContent")
    text = f"{RUBRIC}\n\n--- BUG REPORT ---\nTitle: {title}\n\n{body[:12000]}"
    payload = {"contents": [{"role": "user", "parts": [{"text": text}]}],
               "generationConfig": {"temperature": 0, "responseMimeType": "application/json",
                                    "thinkingConfig": {"thinkingBudget": 512}}}
    for attempt in range(8):
        r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token()}"}, timeout=120)
        if r.status_code == 200:
            d = r.json()
            out = d["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(out), d.get("usageMetadata", {})
        if r.status_code in (429, 500, 503):
            import time
            time.sleep(min(10 * 2 ** attempt, 120))
            continue
        raise RuntimeError(f"{r.status_code} {r.text[:200]}")
    raise RuntimeError("gave up after retries")


def main():
    out = HERE / "labels_sample3500_loose.jsonl"
    done = set()
    if out.exists():
        done = {json.loads(l)["url"] for l in open(out)}
    todo = [json.loads(l) for l in open(HERE / "raw_sample3500.jsonl")]
    todo = [r for r in todo if r["url"] not in done]
    proj = base.project()
    token()  # fetch credentials once before the threads start
    lock = threading.Lock()
    cost = 0.0

    def work(rec):
        res, um = call(rec.get("title") or "", rec.get("body") or "", proj)
        label = str(res.get("label", "")).strip().lower()
        if label not in LABELS:
            label = "none"
        c = (um.get("promptTokenCount", 0) * base.PRICE_IN
             + (um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)) * base.PRICE_OUT) / 1e6
        return {"url": rec["url"], "loose_label": label, "loose_evidence": res.get("evidence", ""),
                "loose_confidence": res.get("confidence"), "model": base.MODEL, "cost_usd": round(c, 6)}

    with open(out, "a") as f, ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(work, r) for r in todo]
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                row = fut.result()
            except Exception as e:  # leave it for a re-run
                print("error:", e, file=sys.stderr)
                continue
            with lock:
                f.write(json.dumps(row, ensure_ascii=False) + "\n"); f.flush()
                cost += row["cost_usd"]
            if i % 250 == 0:
                print(f"{i}/{len(todo)} labelled, ${cost:.2f}", flush=True)
    print(f"done: {len(done) + len(todo)} reports, this run ${cost:.2f}")


if __name__ == "__main__":
    main()
