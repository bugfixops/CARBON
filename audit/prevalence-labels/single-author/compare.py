"""Compare one author's filled audit_sheet.csv with the LLM's labels of the same
100 reports, rubric by rubric (rubrics 1-3; rubric 4 too if its column exists).

For each rubric it prints the number of items, the raw agreement, Cohen's kappa
over the rubric's labels, and Cohen's kappa for the binary question "gesture
(or not_gui) vs. none (or gui)". It also prints kappa pooled over the rubrics
and writes every disagreement to disagreements.csv.

  python compare.py audit_sheet.csv
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parents[2] / "audit" / "prevalence"

GESTURES = ["pinch_zoom", "drag_and_drop", "swipe_region", "quick_tap", "picker_scroll", "multi_touch",
            "scroll", "swipe", "long_press", "double_tap", "orientation"]
# rubric column -> (LLM label file, field, label meaning "no gesture", allowed codes)
RUBRICS = {
    "r1_trigger": ("labels_sample3500_all.jsonl", "llm_label", "none", GESTURES + ["none", "unclear"]),
    "r2_scope": ("labels_sample3500_scope.jsonl", "scope", "gui", ["gui", "not_gui", "unclear"]),
    "r3_any_step": ("labels_sample3500_loose.jsonl", "loose_label", "none", GESTURES + ["none"]),
    "r4_extended": ("labels_sample3500_extended.jsonl", "ext_label", "none",
                    ["fling", "shake", "drawing", "edge_swipe", "one_finger_zoom", "two_finger_rotate", "none"]),
}


def kappa(pairs):
    """Cohen's kappa for a list of (a, b) labels; None when chance agreement is 1."""
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fmt(k):
    return "undefined" if k is None else f"{k:.3f}"


def main(path):
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in reader.fieldnames]
        audit = [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in reader]
    cols = [c for c in RUBRICS if c in header]
    bad = [(r["id"], c, r[c]) for r in audit for c in cols if r[c] and r[c].lower() not in RUBRICS[c][3]]
    if bad:
        sys.exit("unknown codes (see rubric_codes.md): " + "; ".join(f"row {i} {c}={v!r}" for i, c, v in bad))
    pooled, rows = [], []
    print(f"{len(audit)} rows in {path}; rubrics compared: {', '.join(cols)}\n")
    print("| Rubric | Items | Agreement | Cohen's kappa | Binary kappa | LLM non-default | Author non-default |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for col in cols:
        fname, field, default, _ = RUBRICS[col]
        llm = {json.loads(l)["url"]: json.loads(l)[field] for l in open(PREV / fname)}
        pairs = []
        for r in audit:
            a = r[col].lower()
            if not a:
                continue
            if r["url"] not in llm:
                sys.exit(f"no LLM label for {r['url']} ({col})")
            m = llm[r["url"]]
            pairs.append((m, a))
            if m != a:
                rows.append({"id": r["id"], "url": r["url"], "rubric": col, "llm": m, "author": a,
                             "note": r.get("note", "")})
        pooled += [(col + ":" + m, col + ":" + a) for m, a in pairs]
        binary = [(m != default, a != default) for m, a in pairs]
        agree = sum(m == a for m, a in pairs)
        print(f"| {col} | {len(pairs)} | {agree}/{len(pairs)} ({100 * agree / max(len(pairs), 1):.0f}%) "
              f"| {fmt(kappa(pairs))} | {fmt(kappa(binary))} | {sum(b for b, _ in binary)} "
              f"| {sum(b for _, b in binary)} |")
    missing = sum(not r[c] for r in audit for c in cols)
    agree = sum(m == a for m, a in pooled)
    print(f"\nPooled over {len(cols)} rubrics: {len(pooled)} items, agreement {agree}/{len(pooled)}, "
          f"Cohen's kappa {fmt(kappa(pooled))}" + (f" ({missing} empty cells skipped)" if missing else ""))
    with open(HERE / "disagreements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "url", "rubric", "llm", "author", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} disagreements -> disagreements.csv")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python compare.py audit_sheet.csv")
    main(sys.argv[1])
