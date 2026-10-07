"""Gesture prevalence on the 3,500-report sample (make_sample.py). Every report
is labelled (labels_sample3500_all.jsonl, from llm_label.py's rubric), so the
counts need no sampling weights. If verified_labels.csv exists (columns url,
verified_label), the authors' labels replace the LLM's.

A report "needs a gesture" when the action that triggers the bug is a common
gesture (scroll, swipe, long press, double tap) or a complex or precision
gesture (the six below). A device-orientation change is a device action, not a
gesture (the paper's Section 2.1), and is counted separately.

If labels_sample3500_scope.jsonl exists (llm_scope.py), the shares are also
reported over the reports that can be reproduced through an app's GUI, the
population a GUI reproduction tool can act on. That count is conservative: a
gesture report counts only if its scope label is also "gui". Authors' scope
verdicts go in verified_scope.csv (columns url, verified_scope).

  python estimate_sample.py     # prints Markdown tables; writes the two check lists
"""
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPLEX = ["drag_and_drop", "quick_tap", "swipe_region", "pinch_zoom", "picker_scroll", "multi_touch"]
COMMON = ["scroll", "swipe", "long_press", "double_tap"]
NAMES = {"drag_and_drop": "Drag-and-drop", "quick_tap": "Timing-sensitive tap", "swipe_region":
         "Region/coordinate swipe", "pinch_zoom": "Pinch-to-zoom", "picker_scroll": "Picker scroll",
         "multi_touch": "Other multi-finger", "scroll": "Scroll", "swipe": "Swipe", "long_press": "Long press",
         "double_tap": "Double tap", "orientation": "Orientation change (device action)",
         "none": "Tap, text, navigation only", "unclear": "Unclear from the report"}
COVERED = {"drag_and_drop", "quick_tap", "swipe_region", "pinch_zoom", "picker_scroll"}  # CARBON executes as named


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.1f}% ({100 * lo:.1f}–{100 * hi:.1f})"


def main():
    raw = {json.loads(l)["url"]: json.loads(l) for l in open(HERE / "raw_sample3500.jsonl")}
    labels = {json.loads(l)["url"]: json.loads(l) for l in open(HERE / "labels_sample3500_all.jsonl")}
    missing = [u for u in raw if u not in labels]
    verified = {}
    vpath = HERE / "verified_labels.csv"
    if vpath.exists():
        verified = {r["url"]: r["verified_label"] for r in csv.DictReader(vpath.open()) if r.get("verified_label")}
    final = {u: verified.get(u, labels[u]["llm_label"]) for u in raw if u in labels}
    n = len(final)
    c = Counter(final.values())
    g_complex = sum(c[k] for k in COMPLEX)
    g_common = sum(c[k] for k in COMMON)
    g = g_complex + g_common
    print(f"Sample: {len(raw):,} reports; labelled {n:,}; unlabelled {len(missing)}; "
          f"checked by the authors: {sum(u in verified for u in final)}\n")
    print("| Action that triggers the bug | Reports | Share of sample | Share of gesture reports |")
    print("|---|---:|---:|---:|")
    print(f"| **Complex or precision gesture** | **{g_complex}** | {pct(g_complex, n)} | **{pct(g_complex, g)}** |")
    for k in COMPLEX:
        print(f"| &nbsp;&nbsp;{NAMES[k]} | {c[k]} | {100 * c[k] / n:.1f}% | {100 * c[k] / g:.1f}% |")
    print(f"| **Common gesture** | **{g_common}** | {pct(g_common, n)} | {pct(g_common, g)} |")
    for k in COMMON:
        print(f"| &nbsp;&nbsp;{NAMES[k]} | {c[k]} | {100 * c[k] / n:.1f}% | {100 * c[k] / g:.1f}% |")
    print(f"| **Any gesture** | **{g}** | **{pct(g, n)}** | 100% |")
    for k in ["orientation", "none", "unclear"]:
        print(f"| {NAMES[k]} | {c[k]} | {100 * c[k] / n:.1f}% | |")
    print(f"| Total | {n:,} | 100% | |\n")
    cov = sum(c[k] for k in COVERED)
    print(f"CARBON's five gestures that execute as named cover {cov} of the {g_complex} complex-gesture reports.")
    known = n - c["unclear"]
    print(f"Excluding 'unclear' reports ({c['unclear']}): any gesture {pct(g, known)}; "
          f"complex {pct(g_complex, known)} of the decidable reports.")

    # lists for the authors' check
    fields = ["url", "title", "llm_label", "llm_evidence", "verified_label"]
    pos = [u for u in final if labels[u]["llm_label"] in COMPLEX + COMMON + ["orientation"]]
    with open(HERE / "to_verify_sample.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for u in sorted(pos, key=lambda u: (COMPLEX + COMMON + ["orientation"]).index(labels[u]["llm_label"])):
            w.writerow({"url": u, "title": raw[u].get("title", ""), "llm_label": labels[u]["llm_label"],
                        "llm_evidence": labels[u].get("llm_evidence", ""), "verified_label": verified.get(u, "")})
    neg = sorted(u for u in final if labels[u]["llm_label"] == "none")
    pick = random.Random(20261007).sample(neg, min(100, len(neg)))
    with open(HERE / "to_verify_sample_none100.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for u in pick:
            w.writerow({"url": u, "title": raw[u].get("title", ""), "llm_label": "none",
                        "llm_evidence": labels[u].get("llm_evidence", ""), "verified_label": verified.get(u, "")})
    print(f"\nto_verify_sample.csv: {len(pos)} gesture or orientation labels to check; "
          f"to_verify_sample_none100.csv: {len(pick)} random 'none' labels (missed gestures).")
    scope_report(raw, final)


def scope_report(raw, final):
    path = HERE / "labels_sample3500_scope.jsonl"
    if not path.exists():
        return
    scope = {json.loads(l)["url"]: json.loads(l) for l in path.open()}
    vs = HERE / "verified_scope.csv"
    vscope = {r["url"]: r["verified_scope"] for r in csv.DictReader(vs.open()) if r.get("verified_scope")} if vs.exists() else {}
    sc = {u: vscope.get(u, scope[u]["scope"]) for u in final if u in scope}
    n = len(sc)
    cnt = Counter(sc.values())
    gui = [u for u in sc if sc[u] == "gui"]
    ng = len(gui)
    g = sum(final[u] in COMPLEX + COMMON for u in gui)
    cx = sum(final[u] in COMPLEX for u in gui)
    orient = sum(final[u] == "orientation" for u in gui)
    gest_all = [u for u in final if final[u] in COMPLEX + COMMON]
    off = Counter(sc.get(u, "missing") for u in gest_all)
    print(f"\n## Over the GUI-reproducible reports\n")
    print(f"Scope labels: {n:,} (gui {cnt['gui']:,}, not_gui {cnt['not_gui']:,}, unclear {cnt['unclear']:,}); "
          f"checked by the authors: {sum(u in vscope for u in sc)}")
    print(f"Gesture reports by scope label: {dict(off)}\n")
    print("| | Reports | Share |")
    print("|---|---:|---:|")
    print(f"| GUI-reproducible reports | {ng:,} | {pct(ng, n)} of the sample |")
    print(f"| Need a gesture | {g} | **{pct(g, ng)}** of GUI-reproducible reports |")
    print(f"| Need a complex or precision gesture | {cx} | {pct(cx, g)} of those; {pct(cx, ng)} of GUI-reproducible reports |")
    print(f"| Need a gesture or an orientation change | {g + orient} | {pct(g + orient, ng)} of GUI-reproducible reports |")
    notgui = sorted(u for u in sc if scope[u]["scope"] == "not_gui")   # the LLM's labels: the draw must not move
    pick = random.Random(20261007).sample(notgui, min(100, len(notgui)))
    with open(HERE / "to_verify_scope_notgui100.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "title", "scope", "scope_evidence", "verified_scope"]); w.writeheader()
        for u in pick:
            w.writerow({"url": u, "title": raw[u].get("title", ""), "scope": "not_gui",
                        "scope_evidence": scope[u].get("scope_evidence", ""), "verified_scope": vscope.get(u, "")})
    print(f"\nto_verify_scope_notgui100.csv: {len(pick)} random 'not_gui' labels to check (they shrink the base).")


if __name__ == "__main__":
    main()
