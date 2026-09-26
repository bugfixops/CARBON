"""
Audit whether FAILED CARBON runs (timeout / loop) actually executed all the
reproduction steps described in each case's bug_report.txt.

For every log currently classified as a failure we:
  1. Load the matching bug_report.txt and extract:
       - the numbered "Steps to Reproduce" (natural-language step count)
       - the required gesture types (from the "Gestures:" line)
  2. Parse the log's executed action sequence: every line that is a literal
     {'action': ...} dict that the runner echoed AFTER executing it.
  3. Compare:
       - which required gesture types the agent actually performed
       - how many actions it executed vs. how many steps the report lists
       - whether it reached a 'result' verdict (it shouldn't, since these are
         failures — sanity check)
  4. Classify each failed case:
       ALL_GESTURES_DONE   - every required gesture type was performed at least once
       PARTIAL_GESTURES     - some but not all required gesture types performed
       NO_KEY_GESTURE       - the defining gesture (e.g. long_press/pinch/drag) never performed
       NO_ACTIONS           - agent executed no actions at all

Output: Automation/_audit_steps.txt
"""
import os
import re
import ast
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "Dataset" / "carbon-100" / "Results"
DATASET = REPO / "Dataset" / "carbon-100" / "Datasets-CARBON"

# Map bug-report gesture words -> the action verbs the agent emits in logs.
GESTURE_TO_ACTIONS = {
    "long press":  {"long_click"},
    "long_press":  {"long_click"},
    "long-press":  {"long_click"},
    "double tap":  {"double_click", "double_tap"},
    "double_tap":  {"double_click", "double_tap"},
    "double-tap":  {"double_click", "double_tap"},
    "drag":        {"drag", "drag_and_drop", "swipe"},
    "drag and drop": {"drag", "drag_and_drop"},
    "drag_and_drop": {"drag", "drag_and_drop"},
    "pinch":       {"pinch", "pinch_in", "pinch_out", "zoom"},
    "zoom":        {"pinch", "pinch_in", "pinch_out", "zoom"},
    "pinch zoom":  {"pinch", "pinch_in", "pinch_out", "zoom"},
    "scroll":      {"scroll", "swipe"},
    "swipe":       {"swipe", "scroll"},
    "quick tap":   {"click", "double_click"},
    "quick_tap":   {"click", "double_click"},
    "rotate":      {"set_orientation", "rotate"},
    "orientation": {"set_orientation", "rotate"},
    "press":       {"click", "press"},
    "click":       {"click"},
    "tap":         {"click"},
    "type":        {"set_text"},
    "input":       {"set_text"},
    "text":        {"set_text"},
}

# The "defining" gesture per dataset category — the one that MUST be exercised
# for the reproduction to be meaningful.
CATEGORY_KEY_GESTURE = {
    "double_tap":    {"double_click", "double_tap"},
    "long_press":    {"long_click"},
    "drag_and_drop": {"drag", "drag_and_drop"},
    "pinch_zoom":    {"pinch", "pinch_in", "pinch_out", "zoom"},
    "orientation":   {"set_orientation", "rotate"},
    "scroll":        {"scroll", "swipe"},
    "swipe":         {"swipe", "scroll"},
    "quick_tap":     {"click", "double_click"},
}


def read_lines_safe(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception:
        return []


def classify_verdict(lines):
    verdict = "incomplete"
    for ln in lines:
        if "'result':" in ln:
            return "SUCCESS"
        if "LOOP_ABORT" in ln:
            verdict = "FAIL-loop"
        elif "FAILED: exceeded" in ln:
            if verdict != "FAIL-loop":
                verdict = "FAIL-timeout"
    return verdict


def parse_bug_report(path):
    """Return (num_steps, gesture_words:set)."""
    text = ""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0, set()

    # Gestures line, e.g. "Gestures: long press, click, press"
    gestures = set()
    m = re.search(r"^Gestures:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    if m:
        for g in m.group(1).split(","):
            gestures.add(g.strip().lower())

    # Count the numbered steps in the FIRST "Steps to Reproduce" block.
    num_steps = 0
    # find a steps header then count leading "N." lines until a blank/next header
    lines = text.splitlines()
    in_steps = False
    for ln in lines:
        low = ln.strip().lower()
        if low.startswith("steps to reproduce"):
            in_steps = True
            continue
        if in_steps:
            if re.match(r"^\s*\d+[\.\)]\s+\S", ln):
                num_steps += 1
            elif ln.strip() == "" and num_steps > 0:
                break
            elif re.match(r"^\s*[A-Za-z].*:\s*$", ln) and num_steps > 0:
                break
    return num_steps, gestures


def parse_executed_actions(lines):
    """Return list of action-dicts the runner echoed after executing them.

    These are lines that begin with `{'action'` (the runner prints the dict on
    its own line right after execution)."""
    actions = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("{'action'") or s.startswith('{"action"'):
            try:
                d = ast.literal_eval(s)
                if isinstance(d, dict) and "action" in d:
                    actions.append(d.get("action"))
            except Exception:
                m = re.match(r"\{'action':\s*'([^']+)'", s)
                if m:
                    actions.append(m.group(1))
    return actions


def required_action_sets(gesture_words):
    """Map the report's gesture words to sets of acceptable action verbs."""
    req = []
    for g in gesture_words:
        if g in GESTURE_TO_ACTIONS:
            req.append((g, GESTURE_TO_ACTIONS[g]))
    return req


def main():
    out = []
    out.append("==== AUDIT: did FAILED runs execute all bug-report steps? ====")
    out.append("")

    cat_counter = {}
    total_failed = 0
    all_gestures_done = 0
    partial = 0
    no_key = 0
    no_actions = 0

    seen_cases = {}  # (cat,case) -> best classification, to dedupe multiple logs

    for cat_dir in sorted(RESULTS.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith("_") or cat_dir.name.startswith("Results_"):
            continue
        category = cat_dir.name
        for case_dir in sorted(cat_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            case = case_dir.name
            # gather all logs for this case; use the one with the most actions
            logs = sorted(case_dir.glob("*.log"))
            best = None
            for log in logs:
                lines = read_lines_safe(log)
                verdict = classify_verdict(lines)
                if verdict not in ("FAIL-timeout", "FAIL-loop"):
                    continue
                actions = parse_executed_actions(lines)
                if best is None or len(actions) > len(best[2]):
                    best = (log, verdict, actions)
            if best is None:
                continue  # this case has no failed log (maybe success or incomplete)

            log, verdict, actions = best
            # find bug report
            br = DATASET / category / case / "bug_report.txt"
            num_steps, gestures = parse_bug_report(br)
            req = required_action_sets(gestures)
            executed_set = set(actions)

            # which required gestures were satisfied
            satisfied = []
            missing = []
            for gname, verbs in req:
                if executed_set & verbs:
                    satisfied.append(gname)
                else:
                    missing.append(gname)

            key_verbs = CATEGORY_KEY_GESTURE.get(category, set())
            key_done = bool(executed_set & key_verbs) if key_verbs else None

            if len(actions) == 0:
                cls = "NO_ACTIONS"
                no_actions += 1
            elif key_verbs and not key_done:
                cls = "NO_KEY_GESTURE"
                no_key += 1
            elif req and not missing:
                cls = "ALL_GESTURES_DONE"
                all_gestures_done += 1
            elif req and missing:
                cls = "PARTIAL_GESTURES"
                partial += 1
            else:
                # no gesture info in report; fall back to key gesture only
                if key_done:
                    cls = "ALL_GESTURES_DONE"
                    all_gestures_done += 1
                else:
                    cls = "PARTIAL_GESTURES"
                    partial += 1

            total_failed += 1
            cat_counter.setdefault(category, {"ALL_GESTURES_DONE":0,"PARTIAL_GESTURES":0,"NO_KEY_GESTURE":0,"NO_ACTIONS":0})
            cat_counter[category][cls] += 1

            out.append(f"[{verdict}] {category}/{case}")
            out.append(f"    report: {num_steps} steps, gestures={sorted(gestures) if gestures else 'n/a'}")
            out.append(f"    executed {len(actions)} actions; key gesture ({sorted(key_verbs)}) done={key_done}")
            out.append(f"    required gestures satisfied={satisfied} missing={missing}")
            out.append(f"    => {cls}")
            out.append(f"    action sequence: {actions}")
            out.append("")

    out.append("==== SUMMARY ====")
    out.append(f"Failed cases audited: {total_failed}")
    out.append(f"  ALL required gestures executed (report steps done, but bug not confirmed): {all_gestures_done}")
    out.append(f"  PARTIAL gestures (some required gesture never performed): {partial}")
    out.append(f"  KEY gesture for the category NEVER performed: {no_key}")
    out.append(f"  NO actions executed at all: {no_actions}")
    out.append("")
    out.append("By category:")
    for c in sorted(cat_counter):
        s = cat_counter[c]
        out.append(f"  {c:15} ALL={s['ALL_GESTURES_DONE']} PARTIAL={s['PARTIAL_GESTURES']} NO_KEY={s['NO_KEY_GESTURE']} NONE={s['NO_ACTIONS']}")

    outpath = Path(__file__).resolve().parent / "_audit_steps.txt"
    outpath.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {outpath}")


if __name__ == "__main__":
    main()
