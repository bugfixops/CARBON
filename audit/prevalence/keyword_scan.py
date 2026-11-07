"""The keyword scan: a fixed set of regular expressions that assigns each report
one primary gesture and a tier (complex, simple or none). The patterns are those
of the authors' earlier pilot crawl, unchanged. llm_label.py stores the result for
every sampled report as kw_primary and kw_tier in labels_sample3500_all.jsonl, and
count_gestures.py counts a report whose kw_primary is a gesture.
"""
import re

COMPLEX = ["pinch_zoom", "quick_tap", "drag_and_drop", "swipe_region", "picker_scroll", "multi_touch"]
SIMPLE = ["scroll", "swipe", "orientation", "long_press", "double_tap"]

# LENIENT patterns (complex first; priority decides ties).
PATTERNS = [
    ("pinch_zoom",   re.compile(r"\b(pinch|pinch[- ]?to[- ]?zoom|zoom\s*(in|out)|two[- ]?finger\s*zoom)\b", re.I)),
    ("quick_tap",    re.compile(r"\b(tap(p?ing|ped)?\s+(twice|repeatedly|rapidly|multiple\s+times|fast|several\s+times|in\s+quick)|rapid(ly)?\s+tap|quick(ly)?\s+tap|spam(ming)?\s+(tap|click|the\s+button)|tap(p?ing|ped)?\s+too\s+(fast|quick)|click(ing|ed)?\s+(rapidly|too\s+fast)|consecutive\s+tap|in\s+rapid\s+succession|double[- ]?tap\s+(fast|quick))\b", re.I)),
    ("drag_and_drop",re.compile(r"\b(drag\s*(and|&)\s*drop(?!\s+(files|image|video|\w+\s+here|the\s+whole))|drag(ged|ging)?\s+(it|the|a|an|to|from|into)|reorder\w*\s+\w*\s*drag)\b", re.I)),
    ("swipe_region", re.compile(r"\b(edge[- ]?swipe|swipe\s+from\s+(the\s+)?(edge|left|right|screen)|seek\s*bar|seekbar|drag\s+(the\s+)?(slider|handle|seek|thumb|progress)|scrub(bing|bed)?|swipe\s+(at|on|over|across)\s+(a\s+)?(specific|exact|certain|particular))\b", re.I)),
    ("picker_scroll",re.compile(r"\b(number\s*picker|numberpicker|date\s*picker|time\s*picker|datepicker|timepicker|scroll\s*wheel|wheel\s*picker|picker\s+(wheel|dial|scroll|spinner)|scroll.*picker|spin(ner)?\s+(wheel|to\s+select))\b", re.I)),
    ("multi_touch",  re.compile(r"\b(multi[- ]?touch|multitouch|two[- ]?finger|three[- ]?finger|two\s+fingers|three\s+fingers|rotate\s+(the\s+)?(map|image|photo|view|canvas)|rotate\s*gesture|rotation\s*gesture|twist\s+gesture|two\s+pointer)\b", re.I)),
    ("scroll",       re.compile(r"\b(scroll(ed|ing)?|pull[- ]?to[- ]?refresh)\b", re.I)),
    ("swipe",        re.compile(r"\b(swipe|fling|swip(ed|ing))\b", re.I)),
    ("orientation",  re.compile(r"\b(rotat(e|ing)|landscape|portrait|screen\s*rotation|orientation\s*(change|lock))\b", re.I)),
    ("long_press",   re.compile(r"\b(long[- ]?(press|click|tap)|press\s+and\s+hold|hold\s+(down|your\s+finger)|tap\s+and\s+hold)\b", re.I)),
    ("double_tap",   re.compile(r"\b(double[- ]?tap|double[- ]?click|tap(ped|ping)?\s+twice)\b", re.I)),
]
PRIORITY = COMPLEX + SIMPLE


def classify(title, body):
    text = (title or "") + "\n" + (body or "")
    matched = [cat for cat, pat in PATTERNS if pat.search(text)]
    if not matched:
        return "none", "none", []
    primary = min(matched, key=lambda c: PRIORITY.index(c))
    tier = "complex" if primary in COMPLEX else "simple"
    return primary, tier, matched
