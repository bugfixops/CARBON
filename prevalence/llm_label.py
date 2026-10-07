"""Label bug reports with an LLM against a fixed rubric, to measure how accurate
the keyword classifier is (precision on the reports it flags, misses among the
reports it does not flag).

Uses Gemini 2.5 Flash on Vertex AI with Application Default Credentials and the
GCP_PROJECT_ID from the repository's .env. Temperature 0, JSON output, one
call per report; results are cached, so re-runs only label new reports.

  python llm_label.py --input raw_random_bugs.jsonl --select complex --out labels_v1_complex.jsonl
  python llm_label.py --input raw_random_bugs.jsonl --select none --sample 400 --seed 1 --out labels_v1_none.jsonl
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

import google.auth
import google.auth.transport.requests
import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location("v1", HERE / "crawl_gesture_prevalence.py")
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)

MODEL = "gemini-2.5-flash"
PRICE_IN, PRICE_OUT = 0.30, 2.50          # USD per 1M tokens (output includes thinking)
RUBRIC = """You label Android bug reports for a study of GUI gestures.

Decide what the reporter (or a developer) must physically do on the device to
TRIGGER the reported bug. Answer with exactly one label:

Complex or precision gestures:
- pinch_zoom: a two-finger pinch to zoom in or out.
- drag_and_drop: pressing an item or handle and dragging it to a new position
  (reordering a list, moving a widget or icon, dragging into a folder or target).
- swipe_region: a swipe or drag that must start or end at a specific place or
  control: a seek bar or slider, the screen edge, part of a video, a map region.
- quick_tap: taps whose timing matters: rapid repeated taps, tapping during an
  animation or transition, tapping before a timeout or dialog dismissal.
- picker_scroll: scrolling a number, date or time picker wheel to a value.
- multi_touch: any other multi-finger gesture (two-finger swipe or pan,
  rotation, three-finger gestures).
Common gestures and device actions:
- scroll, swipe (a directional swipe anywhere), long_press, double_tap,
  orientation (rotating the device).
Otherwise:
- none: taps, text input and navigation (including back) are enough, or the
  report is not about a GUI interaction (build errors, network, crashes on
  start-up, feature requests).
- unclear: the report does not say enough to decide.

Label a gesture only if the report states or clearly implies that the gesture
is needed to trigger the bug. A gesture that is merely mentioned (e.g. "the zoom
level is wrong" after pressing a + button) does not count.

Reply with JSON only: {"label": "<one label>", "evidence": "<a short quote from
the report, or empty>", "confidence": <0..1>}"""
LABELS = set(v1.COMPLEX) | set(v1.SIMPLE) | {"none", "unclear"}

_creds = None


def token():
    global _creds
    if _creds is None:
        _creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    if not _creds.valid:
        _creds.refresh(google.auth.transport.requests.Request())
    return _creds.token


def project():
    for l in open(HERE.parent / ".env"):
        if l.startswith("GCP_PROJECT_ID="):
            return l.split("=", 1)[1].strip().strip('"')
    raise SystemExit("GCP_PROJECT_ID missing in .env")


def call(title, body, proj):
    url = (f"https://us-central1-aiplatform.googleapis.com/v1/projects/{proj}/locations/us-central1/"
           f"publishers/google/models/{MODEL}:generateContent")
    text = f"{RUBRIC}\n\n--- BUG REPORT ---\nTitle: {title}\n\n{body[:12000]}"
    payload = {"contents": [{"role": "user", "parts": [{"text": text}]}],
               "generationConfig": {"temperature": 0, "responseMimeType": "application/json",
                                    "thinkingConfig": {"thinkingBudget": 512}}}
    for attempt in range(8):
        r = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token()}"}, timeout=120)
        if r.status_code == 200:
            d = r.json()
            um = d.get("usageMetadata", {})
            out = d["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(out), um
        if r.status_code in (429, 500, 503):
            time.sleep(min(10 * 2 ** attempt, 120)); continue
        raise RuntimeError(f"{r.status_code} {r.text[:200]}")
    raise RuntimeError("gave up after retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, nargs="+")
    ap.add_argument("--select", choices=["complex", "simple", "none", "all"], required=True,
                    help="which keyword tier to label")
    ap.add_argument("--sample", type=int, default=0, help="random sample size (0 = all)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--source", help="only records whose source field equals this")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    recs = []
    for p in args.input:
        for line in open(HERE / p if not Path(p).is_absolute() else p):
            r = json.loads(line)
            r.setdefault("source", "github-issue-v1" if Path(p).name == "raw_random_bugs.jsonl" else Path(p).stem)
            if args.source and r["source"] != args.source:
                continue
            primary, tier, _ = v1.classify(r.get("title", ""), r.get("body", ""))
            if args.select == "all" or tier == args.select:
                r["kw_primary"], r["kw_tier"] = primary, tier
                recs.append(r)
    if args.sample and len(recs) > args.sample:
        recs = random.Random(args.seed).sample(recs, args.sample)
    out = HERE / args.out
    done = {json.loads(l)["url"] for l in out.open()} if out.exists() else set()
    proj = project(); cost = 0.0; n = 0
    print(f"{len(recs)} reports selected, {len(done)} already labelled", flush=True)
    with out.open("a") as f:
        for r in recs:
            if r["url"] in done:
                continue
            try:
                lab, um = call(r.get("title", ""), r.get("body", ""), proj)
            except Exception as e:
                print(f"  ERR {r['url']}: {e}", flush=True); continue
            if lab.get("label") not in LABELS:
                lab = {"label": "unclear", "evidence": f"invalid label {lab.get('label')!r}", "confidence": 0}
            c = (um.get("promptTokenCount", 0) * PRICE_IN +
                 (um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)) * PRICE_OUT) / 1e6
            cost += c; n += 1
            f.write(json.dumps({"url": r["url"], "source": r["source"], "kw_primary": r["kw_primary"],
                                "kw_tier": r["kw_tier"], "llm_label": lab["label"],
                                "llm_evidence": lab.get("evidence", ""), "llm_confidence": lab.get("confidence"),
                                "model": MODEL, "cost_usd": round(c, 6)}) + "\n")
            f.flush()
            if n % 25 == 0:
                print(f"  {n} labelled, ${cost:.3f}", flush=True)
    print(f"done: {n} new labels, ${cost:.3f}", flush=True)


if __name__ == "__main__":
    main()
