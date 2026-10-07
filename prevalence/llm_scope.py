"""Label whether each sampled bug report can be reproduced through an app's GUI,
the population a GUI bug-reproduction tool can act on. Complements llm_label.py
(which action triggers the bug): estimate_sample.py reports gesture shares over
all reports and over the GUI-reproducible ones.

Same model and settings as llm_label.py (Gemini 2.5 Flash on Vertex AI,
temperature 0, JSON output); one call per report; resumes from the output file.

  python llm_scope.py --input raw_sample3500.jsonl --out labels_sample3500_scope.jsonl
"""
import argparse
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import llm_label as L  # noqa: E402  (model, prices, credentials, request with retries)

RUBRIC = """You classify Android bug reports for a study of GUI bug reproduction.

Decide whether the reported bug can be reproduced by a person using an app's
user interface on an Android device: launching the app, tapping, typing,
gestures, navigation, rotating the device. The app may be the project's own app
or the sample/demo app of a library. Answer with exactly one label:

- gui: yes. The bug can be triggered through the UI, including crashes on
  launch, visual glitches, and bugs that need particular data, settings,
  accounts, hardware, or network conditions.
- not_gui: no. Triggering it needs something other than using an app's UI:
  build, compile, Gradle or dependency errors; a bug in a library or SDK API
  that only code can trigger; server-side, CI or release problems;
  documentation or translation text; a feature request, enhancement or
  question rather than a bug.
- unclear: the report does not say enough to decide.

When in doubt between gui and not_gui, answer gui.

Reply with JSON only: {"scope": "<gui|not_gui|unclear>", "evidence": "<a short
quote from the report, or empty>", "confidence": <0..1>}"""
SCOPES = {"gui", "not_gui", "unclear"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="raw_sample3500.jsonl")
    ap.add_argument("--out", default="labels_sample3500_scope.jsonl")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    recs = [json.loads(l) for l in open(HERE / args.input)]
    out = HERE / args.out
    done = {json.loads(l)["url"] for l in out.open()} if out.exists() else set()
    todo = [r for r in recs if r["url"] not in done]
    proj = L.project()
    L.RUBRIC = RUBRIC          # llm_label.call() reads its module-level rubric: use this one
    tok_lock, write_lock = threading.Lock(), threading.Lock()
    orig = L.token

    def safe_token():          # llm_label.token() is not thread-safe
        with tok_lock:
            return orig()
    L.token = safe_token
    L.token()
    state = {"n": 0, "cost": 0.0, "err": 0}
    print(f"{len(recs)} reports, {len(done)} already labelled, {len(todo)} to go", flush=True)

    def work(r):
        try:
            lab, um = L.call(r.get("title", ""), r.get("body", ""), proj)
        except Exception as e:
            with write_lock:
                state["err"] += 1
                print(f"  ERR {r['url']}: {e}", flush=True)
            return
        if lab.get("scope") not in SCOPES:
            lab = {"scope": "unclear", "evidence": f"invalid label {lab.get('scope')!r}", "confidence": 0}
        c = (um.get("promptTokenCount", 0) * L.PRICE_IN +
             (um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)) * L.PRICE_OUT) / 1e6
        line = json.dumps({"url": r["url"], "scope": lab["scope"], "scope_evidence": lab.get("evidence", ""),
                           "scope_confidence": lab.get("confidence"), "model": L.MODEL, "cost_usd": round(c, 6)})
        with write_lock:
            with out.open("a") as f:
                f.write(line + "\n")
            state["n"] += 1; state["cost"] += c
            if state["n"] % 250 == 0:
                print(f"  {state['n']} labelled, ${state['cost']:.2f}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(work, todo))
    print(f"done: {state['n']} new labels, ${state['cost']:.2f}, {state['err']} errors", flush=True)


if __name__ == "__main__":
    main()
