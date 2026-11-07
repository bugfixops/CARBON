"""Compare one author's labels for the fourth rubric with the LLM's (paper, Section 2.2).

The author labeled 121 reports (rubric4_audit_filled_author.csv): the 100 random
reports of audit_sheet.csv and the 21 reports to which the fourth rubric gives a
gesture. In this first pass the author used the codes of rubrics 1-3. A code that
is not one of the rubric's six gestures counts as `none`, as the rubric itself
defines (rubric4_codes.md): taps, typing, ordinary scrolls or swipes, pinches,
drags, long presses and device rotation count as none, and so do `not_gui` and
`unclear`. The 17 rows labeled swipe_region or swipe could be one of the six
gestures, so the author labeled them again with the rubric's own codes
(rubric4_recheck_filled_author.csv); these labels replace the first ones.

The script prints the agreement and Cohen's kappa over the 121 reports, over the
100 random ones and over the 21 flagged ones, and writes every disagreement to
rubric4_disagreements.csv.

  python compare_rubric4.py rubric4_audit_filled_author.csv rubric4_recheck_filled_author.csv
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parents[1] / "prevalence"
R4 = ["fling", "shake", "drawing", "edge_swipe", "one_finger_zoom", "two_finger_rotate", "none"]


def kappa(pairs):
    """Cohen's kappa for a list of (a, b) labels; None when chance agreement is 1."""
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def fmt(k):
    return "undefined" if k is None else f"{k:.2f}"


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    col = next(h for h in rows[0] if h.startswith("r4_gesture"))
    return {int(r["id"]): (r["url"], r[col].strip().lower(), r.get("note", "")) for r in rows}


def main(first_path, recheck_path):
    first, again = read(first_path), read(recheck_path)
    bad = [(i, lab) for i, (_, lab, _) in again.items() if lab not in R4]
    if bad or any(i not in first for i in again):
        sys.exit(f"recheck rows need a rubric-4 code and an id of the first sheet: {bad}")
    llm = {json.loads(l)["url"]: json.loads(l)["ext_label"] for l in open(PREV / "labels_sample3500_extended.jsonl")}
    random100 = {r["url"] for r in csv.DictReader(open(HERE / "audit_sheet.csv", encoding="utf-8-sig"))}
    rows, diffs = [], []
    for i, (url, lab, note) in sorted(first.items()):
        author = again[i][1] if i in again else (lab if lab in R4 else "none")
        rows.append((url, llm[url], author))
        if llm[url] != author:
            diffs.append({"id": i, "url": url, "llm": llm[url], "author": author, "first_label": lab,
                          "note": again[i][2] if i in again else note})
    print(f"{len(rows)} reports; {len(again)} labels from the recheck sheet\n")
    print("| Reports | Items | Agreement | Cohen's kappa |")
    print("|---|---:|---:|---:|")
    for name, sel in [("all", rows), ("100 random", [r for r in rows if r[0] in random100]),
                      ("flagged by the LLM", [r for r in rows if r[1] != "none"])]:
        pairs = [(m, a) for _, m, a in sel]
        agree = sum(m == a for m, a in pairs)
        print(f"| {name} | {len(pairs)} | {agree}/{len(pairs)} ({100 * agree / len(pairs):.1f}%) | {fmt(kappa(pairs))} |")
    by = Counter((m, m == a) for _, m, a in rows if m != "none")
    print("\nFlagged reports, by the LLM's label: " + ", ".join(
        f"{g} {by[(g, True)]}/{by[(g, True)] + by[(g, False)]}" for g in R4 if by[(g, True)] + by[(g, False)]))
    with open(HERE / "rubric4_disagreements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "url", "llm", "author", "first_label", "note"])
        w.writeheader()
        w.writerows(diffs)
    print(f"{len(diffs)} disagreements -> rubric4_disagreements.csv")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python compare_rubric4.py rubric4_audit_filled_author.csv rubric4_recheck_filled_author.csv")
    main(sys.argv[1], sys.argv[2])
