"""Single-author audit of the fourth rubric's labels (paper, Section 2.2).

The fourth rubric (prevalence/llm_label_extended.py) labels each report with one
of six rarer gestures (fling, shake, drawing, edge swipe, one-finger zoom,
two-finger rotate) or none. It gives a gesture to only 21 of the 3,500 sampled
reports, none of them among the 100 random reports of audit_sheet.csv, so one
author labeled both: the same 100 reports and all 21.

  python make_rubric4_sheets.py
      writes rubric4_audit_sheet.csv (the 121 reports, shuffled so that the
      flagged ones cannot be told apart) and rubric4_codes.md (the rubric's
      codes). The sheet is blind: it shows no label.

  python make_rubric4_sheets.py --recheck rubric4_audit_filled_author.csv
      writes rubric4_recheck_sheet.csv. The author filled the first sheet with
      the codes of rubrics 1-3 (rubric_codes.md). Its rows labeled swipe_region
      or swipe could be one of the six gestures, so they go on this second
      sheet, which lists the rubric-4 codes in its header.

compare_rubric4.py compares the filled sheets with the LLM's labels. Each row
shows the report's title and the text the LLM saw (the first 12,000 characters
of its body).
"""
import csv
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parents[1] / "prevalence"
SEED, BODY_CHARS = 20261106, 12000
R4_CODES = ["fling", "shake", "drawing", "edge_swipe", "one_finger_zoom", "two_finger_rotate", "none"]
RECHECK = {"swipe_region", "swipe"}

CODES = """# Codes for rubric4_audit_sheet.csv

Fill `r4_gesture` with exactly one code for every row, from the report text
(open the URL for the full report if needed). Leave `note` empty or add a remark.

The question is the rubric's own: does reproducing the bug require one of these
specific gestures, performed on the touch screen or with the device? Count a
gesture only if the report states or clearly implies that it triggers the bug or
is needed to reach the state where the bug shows. The report may describe it in
plain words without naming it.

| Code | Meaning |
|---|---|
| `fling` | a fast swipe that leaves content moving (flinging a list, carousel or page); a normal slow scroll or swipe does NOT count |
| `shake` | physically shaking the device (shake-to-undo, shake-to-silence, shake gesture) |
| `drawing` | drawing or writing with a finger or stylus along a path (strokes on a canvas, whiteboard, signature pad, handwriting, unlock pattern) |
| `edge_swipe` | a swipe starting at the screen edge, including the system back gesture, predictive back, or gesture navigation (swipe up from the bottom edge to go home) |
| `one_finger_zoom` | double-tap and then drag up or down without lifting, to zoom |
| `two_finger_rotate` | two fingers turning around each other to rotate a map, image or view |
| `none` | none of these is needed. Taps, typing, ordinary scrolls or swipes, pinches, drags, long presses and device rotation are labelled by the other rubrics and count as `none` here |
"""


def body_of(r):
    body = re.sub(r"\s+", " ", r.get("body") or "").strip()
    return body[:BODY_CHARS] + " [...]" if len(body) > BODY_CHARS else body


def main():
    raw = {r["url"]: r for r in map(json.loads, open(PREV / "raw_sample3500.jsonl", encoding="utf-8"))}
    ext = {r["url"]: r for r in map(json.loads, open(PREV / "labels_sample3500_extended.jsonl", encoding="utf-8"))}
    random100 = [r["url"] for r in csv.DictReader(open(HERE / "audit_sheet.csv", encoding="utf-8-sig"))]
    flagged = sorted(u for u, r in ext.items() if r["ext_label"] != "none")
    urls = sorted(set(random100) | set(flagged))
    random.Random(SEED).shuffle(urls)
    with open(HERE / "rubric4_audit_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "url", "title", "body_excerpt", "r4_gesture", "note"])
        for n, u in enumerate(urls, 1):
            w.writerow([n, u, raw[u].get("title") or "", body_of(raw[u]), "", ""])
    (HERE / "rubric4_codes.md").write_text(CODES, encoding="utf-8")
    print(f"rubric4_audit_sheet.csv: {len(urls)} reports ({len(random100)} random + {len(flagged)} with a "
          "fourth-rubric gesture); rubric4_codes.md")


def recheck(filled):
    rows = list(csv.DictReader(open(filled, encoding="utf-8-sig")))
    pick = sorted((r for r in rows if r["r4_gesture"].strip() in RECHECK), key=lambda r: int(r["id"]))
    with open(HERE / "rubric4_recheck_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "url", "title", "body_excerpt", "your_first_label",
                    f"r4_gesture ({' | '.join(R4_CODES)})", "note"])
        for r in pick:
            w.writerow([r["id"], r["url"], r["title"], r["body_excerpt"], r["r4_gesture"].strip(), "", ""])
    print(f"rubric4_recheck_sheet.csv: {len(pick)} rows labeled {' or '.join(sorted(RECHECK))}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--recheck":
        recheck(sys.argv[2])
    elif len(sys.argv) == 1:
        main()
    else:
        sys.exit("usage: python make_rubric4_sheets.py [--recheck rubric4_audit_filled_author.csv]")
