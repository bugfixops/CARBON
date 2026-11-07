"""Single-author audit of the prevalence labels (paper, Section 2.2).

Draws 100 reports at random from the 3,500 sampled reports
(prevalence/raw_sample3500.jsonl) with a fixed seed and writes audit_sheet.csv,
on which one author labels each report with rubrics 1-3. The sheet is blind: it
never shows the LLM's labels. compare.py joins the filled sheet with the LLM's
labels and computes Cohen's kappa per rubric. rubric_codes.md lists the codes.

  python make_audit_sheet.py       # writes audit_sheet.csv and rubric_codes.md
"""
import csv
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREV = HERE.parents[2] / "audit" / "prevalence"
SEED, SIZE, BODY_CHARS = 20261102, 100, 1500

CODES = """# Codes for audit_sheet.csv

Fill one code per column for every row, from the report text (open the URL for
the full report). Use exactly these codes. Leave `note` empty or add a remark.

## r1_trigger: what must the reporter do to TRIGGER the bug?
Label a gesture only if the report states or clearly implies that it is needed
to trigger the bug. A gesture that is merely mentioned does not count.

| Code | Meaning |
|---|---|
| `pinch_zoom` | two-finger pinch to zoom in or out |
| `drag_and_drop` | press an item or handle and drag it to a new position (reorder a list, move or resize a widget) |
| `swipe_region` | a swipe or drag that must start or end at a specific place or control: seek bar, slider, screen edge, part of a video, map region |
| `quick_tap` | taps whose timing matters: rapid repeated taps, during an animation or transition, before a timeout |
| `picker_scroll` | turning a number, date or time picker wheel to a value |
| `multi_touch` | any other multi-finger gesture (two-finger swipe or pan, rotation, three fingers) |
| `scroll` | scrolling |
| `swipe` | a directional swipe anywhere |
| `long_press` | long press |
| `double_tap` | double tap |
| `orientation` | rotating the device |
| `none` | taps, typing and navigation (including back) are enough, or the report is not about a GUI interaction |
| `unclear` | the report does not say enough to decide |

## r2_scope: can the bug be reproduced through an app's GUI?

| Code | Meaning |
|---|---|
| `gui` | yes: launching, tapping, typing, gestures, navigation or rotation can trigger it, including crashes on launch, visual glitches, and bugs that need particular data, settings, accounts, hardware or network |
| `not_gui` | no: build, Gradle or dependency errors; a library or SDK bug that only code can trigger; server, CI or release problems; documentation or translation text; a feature request or question |
| `unclear` | the report does not say enough to decide |

When in doubt between `gui` and `not_gui`, choose `gui`.

## r3_any_step: which gesture does ANY step of the reproduction need, including setup?
Be inclusive: count a gesture even if the report only describes it in plain
words ("move the slider", "reorder the items", "resize the widget", "before it
finishes loading"). When in doubt between a gesture and `none`, choose the
gesture. If several gestures could be involved, give the most complex one
(the first group of the r1 table is the complex one).

Codes: the same as r1 without `unclear`: `pinch_zoom`, `drag_and_drop`,
`swipe_region`, `quick_tap`, `picker_scroll`, `multi_touch`, `scroll`, `swipe`,
`long_press`, `double_tap`, `orientation`, `none`.
"""


def main():
    raw = [json.loads(l) for l in open(PREV / "raw_sample3500.jsonl")]
    pick = sorted(random.Random(SEED).sample(range(len(raw)), SIZE))
    with open(HERE / "audit_sheet.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "url", "title", "body_excerpt", "r1_trigger", "r2_scope", "r3_any_step", "note"])
        for n, i in enumerate(pick, 1):
            r = raw[i]
            body = re.sub(r"\s+", " ", r.get("body") or "").strip()
            if len(body) > BODY_CHARS:
                body = body[:BODY_CHARS] + " [...]"
            w.writerow([n, r["url"], r.get("title") or "", body, "", "", "", ""])
    (HERE / "rubric_codes.md").write_text(CODES, encoding="utf-8")
    print(f"{SIZE} of {len(raw)} reports (seed {SEED}) -> audit_sheet.csv, rubric_codes.md")


if __name__ == "__main__":
    main()
