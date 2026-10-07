"""Run the prevalence study's keyword classifier over every collected source
and report the rates per source, with 95% Wilson confidence intervals.

The classifier is v1's `classify()` from crawl_gesture_prevalence.py, unchanged,
so every source is scored by exactly the rules behind the original numbers.

  python classify.py raw_random_bugs.jsonl raw_v2_issues.jsonl raw_v2_prs.jsonl \
                     raw_fdroid_issues.jsonl raw_benchmarks.jsonl
Writes classified_all.csv and prints a Markdown table.
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location("v1", HERE / "crawl_gesture_prevalence.py")
v1 = importlib.util.module_from_spec(spec)
sys.argv_backup = sys.argv
spec.loader.exec_module(v1)
classify, COMPLEX, SIMPLE = v1.classify, v1.COMPLEX, v1.SIMPLE


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def source_of(rec, path):
    if "source" in rec:
        return rec["source"]
    return "github-issue-v1" if path.name == "raw_random_bugs.jsonl" else path.stem


def main(paths):
    rows, by = [], defaultdict(Counter)
    for p in map(Path, paths):
        if not p.exists():
            print(f"(skipping missing {p})", file=sys.stderr); continue
        for line in p.open():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            src = source_of(r, p)
            primary, tier, matched = classify(r.get("title", ""), r.get("body", ""))
            by[src]["n"] += 1; by[src][tier] += 1; by[src]["cat:" + primary] += 1
            rows.append({"source": src, "url": r.get("url"), "repo": f"{r.get('owner')}/{r.get('repo')}",
                         "primary_gesture": primary, "tier": tier, "matched": "|".join(matched)})
    with open(HERE / "classified_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("| Source | Reports | Beyond tap/text | Complex/precision | 95% CI | Complex share of non-basic |")
    print("|---|---:|---:|---:|---:|---:|")
    for src, c in sorted(by.items()):
        n, k, s = c["n"], c["complex"], c["simple"]
        lo, hi = wilson(k, n)
        print(f"| {src} | {n:,} | {k + s:,} ({100 * (k + s) / n:.1f}%) | {k:,} ({100 * k / n:.2f}%) | "
              f"{100 * lo:.2f}–{100 * hi:.2f}% | {100 * k / max(k + s, 1):.1f}% |")
    print()
    print("| Source | " + " | ".join(COMPLEX) + " |")
    print("|---|" + "---:|" * len(COMPLEX))
    for src, c in sorted(by.items()):
        print(f"| {src} | " + " | ".join(str(c['cat:' + k]) for k in COMPLEX) + " |")


if __name__ == "__main__":
    main(sys.argv[1:])
