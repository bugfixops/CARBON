"""Count the gesture reports among the 2,597 GUI-reproducible reports, in the
shape of the paper's prevalence table (Section 2.2).

Base: the 3,500 sampled reports (make_sample.py) whose bug can be reproduced
through the app's GUI by the second rubric (llm_scope.py), with the authors'
verdicts in place of the 100 labels they checked (verified_scope.csv).

Two definitions of "requires a gesture" are counted:

1. Trigger, checked by the authors. The first rubric's label (llm_label.py),
   with the authors' verdicts in place of the labels they checked
   (verified_labels.csv). The authors checked every gesture label of this rubric.
2. Any rubric or a gesture word. A report counts when any of these names a
   gesture: the first rubric (as in 1); the third rubric (llm_label_loose.py:
   any step, including setup); the fourth rubric (llm_label_extended.py); the
   keyword scan (keyword_scan.py, stored as kw_primary); or a gesture word in
   the title or body outside code blocks and log lines (WORDS). The authors
   checked only the first rubric's labels.

A report counts once. It is complex when any of its labels is one of the six
complex gestures, which none of ReBL, AdbGPT and ReActDroid can perform, and is
then listed under its first complex label in the order above; otherwise under
its first common label. A report found only by a gesture word counts as common
and is listed apart. EXTENDED maps the fourth rubric's labels to the table's
rows; a shake, like a device rotation, is a device action and is not counted.

  python count_gestures.py
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

from estimate_sample import pct  # a percentage with its 95% Wilson interval

HERE = Path(__file__).resolve().parent
COMPLEX = ["swipe_region", "drag_and_drop", "quick_tap", "picker_scroll", "pinch_zoom", "multi_touch"]
COMMON = ["scroll", "swipe", "long_press", "double_tap"]
NAMES = {"swipe_region": "Precise swipe", "drag_and_drop": "Drag-and-drop", "quick_tap": "Timing-sensitive tap",
         "picker_scroll": "Picker-wheel turn", "pinch_zoom": "Pinch-to-zoom", "multi_touch": "Other multi-finger",
         "scroll": "Scroll", "swipe": "Swipe", "long_press": "Long press", "double_tap": "Double tap"}
EXTENDED = {"edge_swipe": "swipe_region", "drawing": "swipe_region", "one_finger_zoom": "pinch_zoom",
            "two_finger_rotate": "multi_touch", "fling": "swipe"}  # shake: a device action, not counted
WORDS = re.compile(
    r"\b(scroll(?:ing|ed|s)?|swip(?:e|es|ed|ing)|long[- ]?press(?:es|ed|ing)?|press(?:ing)? and hold"
    r"|tap(?:ping)? and hold|hold(?:ing)? down|double[- ]?tap(?:s|ped|ping)?|tap(?:ping)? twice"
    r"|drag(?:s|ged|ging)?|drop(?:ped|ping)? (?:it|the|onto|into)|pinch(?:es|ed|ing)?|zoom(?:s|ed|ing)? (?:in|out)"
    r"|two[- ]finger|multi[- ]?touch|fling(?:s|ing)?|flick(?:s|ed|ing)?|slid(?:e|es|ing)"
    r"|pull(?:ing)?(?: down)? to refresh|pull(?:ing)? down|gestures?)\b", re.I)
LOG_LINE = re.compile(r"^(at |\d{2}-\d{2} |E/|W/|D/|I/|Caused by|java\.|android\.|kotlin\.)")


def prose(text):
    """The report text without fenced code blocks and stack-trace or log lines."""
    out, in_code = [], False
    for line in (text or "").splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or LOG_LINE.match(line.strip()) or "Exception" in line:
            continue
        out.append(line)
    return "\n".join(out)


def jsonl(name):
    return {json.loads(l)["url"]: json.loads(l) for l in open(HERE / name)}


def verdicts(name, column):
    return {r["url"]: r[column] for r in csv.DictReader(open(HERE / name)) if r.get(column)}


def table(title, counts, word_only, base):
    cx = sum(counts[k] for k in COMPLEX)
    cm = sum(counts[k] for k in COMMON) + word_only
    g = cx + cm
    print(f"## {title}\n")
    print("| Gesture | Reports | Of gesture reports |")
    print("|---|---:|---:|")
    print(f"| **Complex gesture** | **{cx}** | **{pct(cx, g)}** |")
    for k in COMPLEX:
        print(f"| &nbsp;&nbsp;{NAMES[k]} | {counts[k]} | {100 * counts[k] / g:.1f}% |")
    print(f"| **Common gesture** | **{cm}** | {pct(cm, g)} |")
    for k in COMMON:
        print(f"| &nbsp;&nbsp;{NAMES[k]} | {counts[k]} | {100 * counts[k] / g:.1f}% |")
    if word_only:
        print(f"| &nbsp;&nbsp;Gesture word only | {word_only} | {100 * word_only / g:.1f}% |")
    print(f"| **Reports that need a gesture** | **{g}** | 100% |")
    print(f"| Total bug reports | {base:,} | |\n")
    print(f"{g} of the {base:,} reports need a gesture, {pct(g, base)}; "
          f"{cx} need a complex one, {pct(cx, base)}.\n")


def main():
    raw = jsonl("raw_sample3500.jsonl")
    first = jsonl("labels_sample3500_all.jsonl")
    scope = jsonl("labels_sample3500_scope.jsonl")
    third = jsonl("labels_sample3500_loose.jsonl")
    fourth = jsonl("labels_sample3500_extended.jsonl")
    v_first = verdicts("verified_labels.csv", "verified_label")
    v_scope = verdicts("verified_scope.csv", "verified_scope")

    sc = {u: v_scope.get(u, scope[u]["scope"]) for u in raw}
    n = Counter(sc.values())
    to_gui = sum(v_scope[u] == "gui" and scope[u]["scope"] != "gui" for u in v_scope)
    gui = [u for u in raw if sc[u] == "gui"]
    print(f"{len(raw):,} sampled reports. Second rubric, with the authors' verdicts on {len(v_scope)} of its "
          f"labels ({to_gui} changed to gui): gui {n['gui']:,}, not_gui {n['not_gui']:,}, unclear {n['unclear']:,}. "
          f"The base is the {len(gui):,} gui reports.\n")

    trigger = {u: v_first.get(u, first[u]["llm_label"]) for u in gui}
    table("1. Trigger, checked by the authors", Counter(trigger.values()), 0, len(gui))

    counts, word_only = Counter(), 0
    for u in gui:
        labels = [trigger[u], third[u]["loose_label"], EXTENDED.get(fourth[u]["ext_label"]), first[u]["kw_primary"]]
        labels = [l for l in labels if l in COMPLEX + COMMON]
        if labels:
            counts[next((l for l in labels if l in COMPLEX), labels[0])] += 1
        elif WORDS.search((raw[u].get("title") or "") + "\n" + prose(raw[u].get("body"))):
            word_only += 1
    table("2. Any rubric or a gesture word (only the first rubric's labels were checked)", counts, word_only, len(gui))


if __name__ == "__main__":
    main()
