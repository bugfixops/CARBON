"""Estimate the share of bug reports that need a complex or precision gesture,
per source, correcting the keyword classifier with LLM labels (and, once the
authors have checked them, with the authors' verdicts).

Design (two-phase stratified estimate, per source):
  * stratum = the keyword classifier's tier (complex / simple / none);
  * in each stratum, a census or a random sample was labelled (llm_label.py);
  * estimated complex reports = sum over strata of N_stratum * (positives / labelled),
    with a normal-approximation 95% CI and a finite-population correction.

If verified_labels.csv exists (columns: url, verified_label), its labels
replace the LLM's for those reports.

  python estimate.py            # prints Markdown tables, writes to_verify.csv
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPLEX = ["pinch_zoom", "quick_tap", "drag_and_drop", "swipe_region", "picker_scroll", "multi_touch"]

# source -> (raw files, {tier: label file})
SOURCES = {
    "GitHub issues (v1 sample)": (["raw_random_bugs.jsonl"], "github-issue-v1",
                                  {"complex": "labels_v1_complex.jsonl", "simple": "labels_v1_simple.jsonl",
                                   "none": "labels_v1_none_sample.jsonl"}),
    "GitHub issues (v2 sample)": (["raw_v2_issues.jsonl"], "github-issue",
                                  {"complex": "labels_v2_complex.jsonl", "simple": "labels_v2_simple.jsonl",
                                   "none": "labels_v2_none_sample.jsonl"}),
    "GitHub fix PRs (v2 repos)": (["raw_v2_prs.jsonl"], "github-fix-pr",
                                  {"complex": "labels_pr_complex.jsonl", "simple": "labels_pr_simple.jsonl",
                                   "none": "labels_pr_none_sample.jsonl"}),
    "F-Droid apps, GitLab/Codeberg": (["raw_fdroid_issues.jsonl"], None,
                                      {"complex": "labels_fdroid_complex.jsonl", "simple": "labels_fdroid_simple.jsonl",
                                       "none": "labels_fdroid_none_sample.jsonl"}),
    "ReActDroid crash reports": (["raw_benchmarks.jsonl"], "benchmark-reactdroid-motivation",
                                 {"complex": "labels_rd_complex.jsonl", "simple": "labels_rd_simple.jsonl",
                                  "none": "labels_rd_none_sample.jsonl"}),
    "AndroR2 benchmark": (["raw_benchmarks.jsonl"], "benchmark-andror2", {"all": "labels_andror2_all.jsonl"}),
    "ReCDroid benchmark": (["raw_benchmarks.jsonl"], "benchmark-recdroid", {"all": "labels_recdroid_all.jsonl"}),
    "Themis benchmark": (["raw_benchmarks.jsonl"], "benchmark-themis", {"all": "labels_themis_all.jsonl"}),
    "ReBL benchmark": (["raw_benchmarks.jsonl"], "benchmark-rebl", {"all": "labels_rebl_all.jsonl"}),
}

sys.path.insert(0, str(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location("v1", HERE / "crawl_gesture_prevalence.py")
v1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v1)


def tiers(raw_files, source):
    n = Counter()
    for f in raw_files:
        for line in open(HERE / f):
            r = json.loads(line)
            src = r.get("source", "github-issue-v1")
            if source and src != source:
                continue
            _, tier, _ = v1.classify(r.get("title", ""), r.get("body", ""))
            n[tier] += 1; n["all"] += 1
    return n


def load(f, verified):
    p = HERE / f
    if not p.exists():
        return None
    out = []
    for line in p.open():
        x = json.loads(line)
        x["final_label"] = verified.get(x["url"], x["llm_label"])
        out.append(x)
    return out


def main():
    verified = {}
    vpath = HERE / "verified_labels.csv"
    if vpath.exists():
        verified = {r["url"]: r["verified_label"] for r in csv.DictReader(vpath.open()) if r.get("verified_label")}
    to_verify, cats = [], defaultdict(Counter)
    print(f"Labels checked by the authors: {len(verified)}\n")
    print("| Source | Reports | Keyword estimate | Corrected estimate (95% CI) | Beyond tap/text: keyword → corrected | Labelled |")
    print("|---|---:|---:|---:|---:|---:|")
    for name, (raw, source, files) in SOURCES.items():
        n = tiers(raw, source)
        est, var, labelled, complete = 0.0, 0.0, 0, True
        est_any = 0.0
        for tier, f in files.items():
            L = load(f, verified)
            if L is None:
                complete = False; continue
            N = n[tier]; m = len(L); labelled += m
            k = sum(x["final_label"] in COMPLEX for x in L)
            if m == 0:
                continue
            p = k / m
            est += N * p
            est_any += N * sum(x["final_label"] not in ("none", "unclear") for x in L) / m
            if m < N:
                var += N * N * p * (1 - p) / m * (1 - m / N)
            for x in L:
                if x["final_label"] in COMPLEX:
                    cats[name][x["final_label"]] += N / m
                if x["llm_label"] in COMPLEX:
                    to_verify.append({"source": name, "url": x["url"], "keyword_tier": x["kw_tier"],
                                      "keyword_category": x["kw_primary"], "llm_label": x["llm_label"],
                                      "llm_evidence": x["llm_evidence"], "verified_label": verified.get(x["url"], "")})
        N = n["all"]
        kw = n["complex"]
        se = math.sqrt(var)
        lo, hi = max(0.0, est - 1.96 * se), est + 1.96 * se
        flag = "" if complete else " (labelling incomplete)"
        any_kw = n["complex"] + n["simple"]
        print(f"| {name} | {N:,} | {kw} ({100 * kw / N:.2f}%) | {est:.0f} ({100 * est / N:.2f}%; "
              f"{100 * lo / N:.2f}–{100 * hi / N:.2f}%){flag} | {100 * any_kw / N:.1f}% → {100 * est_any / N:.1f}% | {labelled:,} |")
    print("\nEstimated complex reports by gesture (scaled by sampling weights):\n")
    print("| Source | " + " | ".join(COMPLEX) + " |")
    print("|---|" + "---:|" * len(COMPLEX))
    for name in SOURCES:
        print(f"| {name} | " + " | ".join(f"{cats[name][c]:.0f}" for c in COMPLEX) + " |")
    with open(HERE / "to_verify.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "url", "keyword_tier", "keyword_category", "llm_label",
                                          "llm_evidence", "verified_label"])
        w.writeheader(); w.writerows(to_verify)
    print(f"\nto_verify.csv: {len(to_verify)} LLM-positive reports for the authors to check "
          f"(fill verified_label with a complex label, a simple label, or none).")


if __name__ == "__main__":
    main()
