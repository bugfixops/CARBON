"""Build check_labels.html, an offline page for the authors' check of the LLM
labels (to_verify_sample.csv, to_verify_sample_none100.csv,
to_verify_scope_notgui100.csv). Each author opens it in a browser, gives a
verdict for every item, and exports a CSV; agreement.py then computes Cohen's
kappa and writes verified_labels.csv and verified_scope.csv.

  python make_check_page.py
"""
import csv
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GP = HERE.parent
TRIGGER = ["drag_and_drop", "quick_tap", "swipe_region", "pinch_zoom", "picker_scroll", "multi_touch",
           "scroll", "swipe", "long_press", "double_tap", "orientation", "none", "unclear"]
SCOPE = ["gui", "not_gui", "unclear"]


def main():
    raw = {json.loads(l)["url"]: json.loads(l) for l in open(GP / "raw_sample3500.jsonl")}
    items = []
    for fname, kind, label_col, quote_col in [("to_verify_sample.csv", "trigger", "llm_label", "llm_evidence"),
                                               ("to_verify_sample_none100.csv", "trigger", "llm_label", "llm_evidence"),
                                               ("to_verify_scope_notgui100.csv", "scope", "scope", "scope_evidence")]:
        for r in csv.DictReader(open(GP / fname)):
            rec = raw.get(r["url"], {})
            items.append({"list": fname.removesuffix(".csv"), "kind": kind, "url": r["url"],
                          "title": rec.get("title", r.get("title", "")), "body": (rec.get("body") or "")[:1500],
                          "llm": r[label_col], "quote": r.get(quote_col, "")})
    page = TEMPLATE.replace("__ITEMS__", json.dumps(items).replace("</", "<\\/")) \
                   .replace("__TRIGGER__", json.dumps(TRIGGER)).replace("__SCOPE__", json.dumps(SCOPE))
    (HERE / "check_labels.html").write_text(page, encoding="utf-8")
    print(f"check_labels.html: {len(items)} items")


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Label check</title>
<style>
:root { --bg:#fff; --fg:#1d1d1f; --muted:#666; --line:#ddd; --card:#f7f7f8; --accent:#0b57d0; }
@media (prefers-color-scheme: dark) { :root { --bg:#151517; --fg:#ececf0; --muted:#a0a0a8; --line:#33333a; --card:#1f1f23; --accent:#8ab4f8; } }
body { background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, sans-serif; margin:0; padding:16px; }
header { position:sticky; top:0; background:var(--bg); padding:8px 0 12px; border-bottom:1px solid var(--line); z-index:1; }
.card { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px; margin:12px 0; max-width:900px; }
.card.done { opacity:.6; } .meta { color:var(--muted); font-size:13px; }
pre { white-space:pre-wrap; max-height:180px; overflow:auto; font-size:13px; background:var(--bg); padding:8px; border-radius:6px; }
button, select, input { font:inherit; padding:4px 8px; } a { color:var(--accent); }
</style></head><body>
<header>
  <b>Label check</b> &middot; rater: <input id="rater" placeholder="your initials" size="8">
  &middot; <span id="progress"></span> &middot; <label><input type="checkbox" id="hideDone"> hide done</label>
  &middot; <button id="export">Export CSV</button>
  <div class="meta">For each report: is the LLM's label right? "Agree", or pick the correct label. Trigger labels:
  the action the reporter must perform to <i>trigger</i> the bug. Scope labels: can the bug be reproduced through an app's GUI at all?</div>
</header>
<main id="list"></main>
<script>
const ITEMS = __ITEMS__, TRIGGER = __TRIGGER__, SCOPE = __SCOPE__;
const KEY = "label-check-v1";
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { state = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
const rater = document.getElementById("rater");
rater.value = state.__rater || ""; rater.oninput = () => { state.__rater = rater.value; save(); };
const keyOf = it => it.list + "|" + it.url;
function render() {
  const list = document.getElementById("list"); list.textContent = "";
  const hide = document.getElementById("hideDone").checked;
  let done = 0;
  ITEMS.forEach((it, i) => {
    const v = state[keyOf(it)]; if (v) done++;
    if (hide && v) return;
    const c = document.createElement("div"); c.className = "card" + (v ? " done" : "");
    const h = document.createElement("div"); h.innerHTML = "<b></b> <span class=meta></span>";
    h.querySelector("b").textContent = (i + 1) + ". " + it.title;
    h.querySelector(".meta").textContent = "[" + it.list + "]";
    const a = document.createElement("a"); a.href = it.url; a.target = "_blank"; a.rel = "noopener"; a.textContent = it.url;
    const q = document.createElement("div"); q.className = "meta";
    q.textContent = "LLM: " + it.llm + (it.quote ? '  \\u2014 "' + it.quote + '"' : "");
    const pre = document.createElement("pre"); pre.textContent = it.body;
    const row = document.createElement("div");
    const agree = document.createElement("button"); agree.textContent = "Agree (" + it.llm + ")";
    agree.onclick = () => { state[keyOf(it)] = it.llm; save(); render(); };
    const sel = document.createElement("select");
    ["(other label)"].concat(it.kind === "scope" ? SCOPE : TRIGGER).forEach(o => { const op = document.createElement("option"); op.textContent = o; sel.appendChild(op); });
    if (v && v !== it.llm) sel.value = v;
    sel.onchange = () => { if (sel.selectedIndex > 0) { state[keyOf(it)] = sel.value; save(); render(); } };
    const st = document.createElement("span"); st.className = "meta"; st.textContent = v ? "  your verdict: " + v : "";
    row.append(agree, " ", sel, st);
    c.append(h, a, q, pre, row); list.appendChild(c);
  });
  document.getElementById("progress").textContent = done + " / " + ITEMS.length + " done";
}
document.getElementById("hideDone").onchange = render;
document.getElementById("export").onclick = () => {
  const esc = s => '"' + String(s).replace(/"/g, '""') + '"';
  const lines = ["rater,list,url,kind,llm_label,verdict"].concat(ITEMS.map(it =>
    [state.__rater || "", it.list, it.url, it.kind, it.llm, state[keyOf(it)] || ""].map(esc).join(",")));
  const blob = new Blob([lines.join("\\n") + "\\n"], {type: "text/csv"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = "labels_" + (state.__rater || "rater") + ".csv"; a.click();
};
render();
</script></body></html>
"""

if __name__ == "__main__":
    main()
