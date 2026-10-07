"""Build recheck.html: the items the two authors settle together after their
independent labelling (ratings_rater1.csv, ratings_rater2.csv):
  * every item where their verdicts differ;
  * every item both changed to quick_tap although the LLM said otherwise
    (quick_tap means a tap whose timing matters, not an ordinary tap).
The page exports each item's settled label; recheck_final.csv records both raters'
answers, the settled label, and a note where the rubric decided it. agreement.py
takes it as --resolved.

  python make_recheck_page.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GP = HERE.parent
TRIGGER = ["none", "drag_and_drop", "quick_tap", "swipe_region", "pinch_zoom", "picker_scroll", "multi_touch",
           "scroll", "swipe", "long_press", "double_tap", "orientation", "unclear"]
SCOPE = ["gui", "not_gui", "unclear"]


def main():
    raw = {json.loads(l)["url"]: json.loads(l) for l in open(GP / "raw_sample3500.jsonl")}
    a = {(r["list"], r["url"]): r for r in csv.DictReader(open(HERE / "ratings_rater1.csv"))}
    b = {(r["list"], r["url"]): r for r in csv.DictReader(open(HERE / "ratings_rater2.csv"))}
    items = []
    for k in sorted(a):
        va, vb, llm = a[k]["verdict"], b[k]["verdict"], a[k]["llm_label"]
        if va != vb:
            why = "you disagree"
        elif va == "quick_tap" and llm != "quick_tap":
            why = "quick_tap: does the timing of the tap matter?"
        else:
            continue
        rec = raw.get(k[1], {})
        items.append({"list": k[0], "url": k[1], "kind": a[k]["kind"], "llm": llm, "a": va, "b": vb, "why": why,
                      "title": rec.get("title", ""), "body": (rec.get("body") or "")[:1500]})
    page = TEMPLATE.replace("__ITEMS__", json.dumps(items).replace("</", "<\\/")) \
                   .replace("__TRIGGER__", json.dumps(TRIGGER)).replace("__SCOPE__", json.dumps(SCOPE))
    (HERE / "recheck.html").write_text(page, encoding="utf-8")
    print(f"recheck.html: {len(items)} items "
          f"({sum(i['why'] == 'you disagree' for i in items)} disagreements, "
          f"{sum(i['why'] != 'you disagree' for i in items)} quick_tap)")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Label re-check</title>
<style>
:root { --bg:#fff; --fg:#1d1d1f; --muted:#666; --line:#ddd; --card:#f7f7f8; --accent:#0b57d0; --warn:#b3261e; }
@media (prefers-color-scheme: dark) { :root { --bg:#151517; --fg:#ececf0; --muted:#a0a0a8; --line:#33333a; --card:#1f1f23; --accent:#8ab4f8; --warn:#f2b8b5; } }
body { background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; margin:0; padding:16px; }
header { position:sticky; top:0; background:var(--bg); padding:8px 0 12px; border-bottom:1px solid var(--line); z-index:1; }
.rubric { max-width:900px; border:1px solid var(--line); border-radius:8px; padding:8px 14px; margin:12px 0; font-size:14px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px; margin:12px 0; max-width:900px; }
.card.done { opacity:.6; } .meta { color:var(--muted); font-size:13px; } .why { color:var(--warn); font-weight:600; }
pre { white-space:pre-wrap; max-height:180px; overflow:auto; font-size:13px; background:var(--bg); padding:8px; border-radius:6px; }
button, select { font:inherit; padding:4px 8px; } a { color:var(--accent); }
</style></head><body>
<header><b>Label re-check (decide together)</b> &middot; <span id="progress"></span>
 &middot; <label><input type="checkbox" id="hideDone"> hide done</label> &middot; <button id="export">Export CSV</button></header>
<div class="rubric">
<b>Trigger labels: the action the reporter must perform to <i>trigger</i> the bug.</b><br>
<b>none</b>: ordinary taps, text input and navigation (including back) are enough, <b>an ordinary tap is "none"</b>;
or the report is not about a GUI interaction (build or install errors, network, start-up crashes, feature requests).<br>
<b>quick_tap</b>: only when the <b>timing</b> of the taps matters: rapid repeated taps, tapping during an animation or
transition, tapping before a timeout or a dialog closes.<br>
<b>Complex or precision:</b> pinch_zoom (two-finger pinch) &middot; drag_and_drop (press an item or handle and drag it) &middot;
swipe_region (a swipe that must start or end at a specific place: slider, seek bar, screen edge, part of a video, a map region)
&middot; picker_scroll (turn a number, date or time wheel to a value) &middot; multi_touch (other multi-finger gestures).<br>
<b>Common:</b> scroll, swipe (a directional swipe anywhere), long_press, double_tap. <b>Device action:</b> orientation.
<b>unclear</b>: the report does not say enough.<br>
<b>Scope labels:</b> gui (can be reproduced through an app's UI) &middot; not_gui (build/Gradle errors, library API bugs needing
code, server or CI problems, docs, feature requests) &middot; unclear.
</div>
<main id="list"></main>
<script>
const ITEMS = __ITEMS__, TRIGGER = __TRIGGER__, SCOPE = __SCOPE__;
const KEY = "label-recheck-v1";
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { state = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
const keyOf = it => it.list + "|" + it.url;
function render() {
  const list = document.getElementById("list"); list.textContent = "";
  const hide = document.getElementById("hideDone").checked; let done = 0;
  ITEMS.forEach((it, i) => {
    const v = state[keyOf(it)]; if (v) done++;
    if (hide && v) return;
    const c = document.createElement("div"); c.className = "card" + (v ? " done" : "");
    const h = document.createElement("div"); const t = document.createElement("b");
    t.textContent = (i + 1) + ". " + it.title; h.appendChild(t);
    const w = document.createElement("div"); w.className = "why"; w.textContent = it.why;
    const a = document.createElement("a"); a.href = it.url; a.target = "_blank"; a.rel = "noopener"; a.textContent = it.url;
    const m = document.createElement("div"); m.className = "meta";
    m.textContent = "[" + it.list + "]  LLM: " + it.llm + "  |  rater 1: " + it.a + "  |  rater 2: " + it.b;
    const pre = document.createElement("pre"); pre.textContent = it.body;
    const row = document.createElement("div");
    const sel = document.createElement("select");
    ["(final label)"].concat(it.kind === "scope" ? SCOPE : TRIGGER).forEach(o => { const op = document.createElement("option"); op.textContent = o; sel.appendChild(op); });
    if (v) sel.value = v;
    sel.onchange = () => { if (sel.selectedIndex > 0) { state[keyOf(it)] = sel.value; save(); render(); } };
    const st = document.createElement("span"); st.className = "meta"; st.textContent = v ? "  final: " + v : "";
    row.append(sel, st);
    c.append(h, w, a, m, pre, row); list.appendChild(c);
  });
  document.getElementById("progress").textContent = done + " / " + ITEMS.length + " decided";
}
document.getElementById("hideDone").onchange = render;
document.getElementById("export").onclick = () => {
  const esc = s => '"' + String(s).replace(/"/g, '""') + '"';
  const lines = ["list,url,kind,llm_label,rater_a,rater_b,final"].concat(ITEMS.map(it =>
    [it.list, it.url, it.kind, it.llm, it.a, it.b, state[keyOf(it)] || ""].map(esc).join(",")));
  const blob = new Blob([lines.join("\\n") + "\\n"], {type: "text/csv"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "recheck_final.csv"; a.click();
};
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
