"""Summarise a results folder (local, or merged from all CI jobs).

  python harness/summarize.py [--out baselines/results] [--markdown summary.md]

Writes, per tool:
  results/<tool>/runs.csv    one row per run, rebuilt from every run.json
  results/<tool>/audit.csv   the audit sheet: two empty reviewer columns per run
and prints a Markdown summary (status counts, tool claims, app crashes, cost),
optionally also to a file such as $GITHUB_STEP_SUMMARY.
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from harness.run_baselines import SUMMARY_FIELDS, display_path  # noqa: E402

AUDIT_FIELDS = ["tool", "case", "category", "crash_bug", "status", "tool_claim", "app_crash_or_anr",
                "version_matches_report", "run_dir", "reviewer_1", "reviewer_2", "final_verdict", "notes"]


def load_runs(root, tool):
    runs = []
    for p in sorted((root / tool).glob("*/*/run.json")):
        rec = json.loads(p.read_text())
        rec["_dir"] = p.parent
        runs.append(rec)
    return runs


def row(rec):
    llm = rec.get("llm", {})
    return {"case": rec["case"], "category": rec["category"], "crash_bug": rec["crash_bug"],
            "status": rec.get("status"), "tool_claim": rec.get("tool_claim"),
            "app_crash_or_anr": rec.get("logcat", {}).get("app_crash_or_anr"),
            "duration_s": rec.get("duration_s"), "llm_calls": llm.get("calls"),
            "prompt_tokens": llm.get("prompt_tokens"), "output_tokens": llm.get("output_tokens"),
            "thought_tokens": llm.get("thought_tokens"), "cost_usd": llm.get("cost_usd"),
            "verdict": rec.get("verdict"), "run_dir": display_path(rec["_dir"])}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(HERE.parent / "results"))
    p.add_argument("--markdown", help="also append the summary to this file")
    args = p.parse_args()
    root = Path(args.out)

    lines = ["## Retest (Gemini 2.5 Pro)", ""]
    grand = 0.0
    for tool in ("adbgpt", "reactdroid", "carbon"):
        runs = load_runs(root, tool)
        if not runs:
            continue
        rows = [row(r) for r in runs]
        with open(root / tool / "runs.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
            w.writeheader()
            w.writerows(rows)
        with open(root / tool / "audit.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=AUDIT_FIELDS)
            w.writeheader()
            for rec, r in zip(runs, rows):
                w.writerow({"tool": tool, "case": r["case"], "category": r["category"],
                            "crash_bug": r["crash_bug"], "status": r["status"], "tool_claim": r["tool_claim"],
                            "app_crash_or_anr": r["app_crash_or_anr"],
                            "version_matches_report": rec.get("version_matches_report"),
                            "run_dir": r["run_dir"]})
        status = collections.Counter(r["status"] for r in rows)
        claims = sum(1 for r in rows if r["tool_claim"])
        app_crash = sum(1 for r in rows if r["app_crash_or_anr"])
        mismatched = [r["case"] for r, rec in zip(rows, runs) if rec.get("version_matches_report") is False]
        cost = sum(r["cost_usd"] or 0 for r in rows)
        grand += cost
        lines += [f"### {tool}: {len(rows)} runs over {len({r['case'] for r in rows})} cases", "",
                  "| | |", "|---|---|",
                  "| Status | " + ", ".join(f"{k} {v}" for k, v in sorted(status.items())) + " |",
                  f"| Tool's own claim | {claims} |",
                  f"| Crash/ANR in the app's own process (logcat) | {app_crash} |",
                  f"| LLM cost | ${cost:.2f} (${cost / len(rows):.3f} per run) |",
                  f"| Installed version differs from report | {len(mismatched)}"
                  + (f": {', '.join(mismatched[:10])}" if mismatched else "") + " |",
                  "", "Every run is PENDING_AUDIT; fill in `audit.csv` (two reviewers).", ""]
    lines.append(f"**Total LLM cost: ${grand:.2f}**")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.markdown:
        with open(args.markdown, "a") as f:
            f.write(text)


if __name__ == "__main__":
    main()
