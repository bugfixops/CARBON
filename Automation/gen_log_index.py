"""
Generate a markdown table with clickable links to per-case .log files for both
runs:
  - OpenAI gpt-4o : Dataset/carbon-100/Results/<cat>/<case>/<timestamp>.log
  - Gemini/CARBON : Dataset/<cat>/<case>/carbon_log.txt  (gemini-2.5-pro baseline)

Also reads the CARBON verdict from Dataset/<cat>/test_report.md when present.
Writes run_logs_index.md at the repo root with repo-root-relative, URL-encoded
links so they open the actual .log file when clicked.
"""
import os
import re
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "Dataset" / "carbon-100" / "Results"
GEMINI_ROOT = REPO / "Dataset"

CATEGORIES = ["double_tap", "drag_and_drop", "long_press", "orientation",
              "pinch_zoom", "quick_tap", "scroll", "swipe"]


def read_lines_safe(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception:
        return []


def openai_verdict(logpath):
    v = "incomplete"
    for ln in read_lines_safe(logpath):
        if "'result':" in ln:
            return "SUCCESS"
        if "LOOP_ABORT" in ln:
            v = "FAIL-loop"
        elif "FAILED: exceeded" in ln and v != "FAIL-loop":
            v = "FAIL-timeout"
    return v


def rel_link(path):
    """repo-root-relative, URL-encoded path for a markdown link."""
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")
    # encode each segment but keep the slashes
    return "/".join(quote(seg) for seg in rel.split("/"))


def gemini_log_verdict(logpath):
    """Derive the CARBON/gemini verdict directly from the carbon_log.txt.

    Returns one of: 'PASS', 'FAIL', 'RAN' (ran but no explicit result line),
    or None if the file is missing/empty.
    """
    if not logpath.is_file() or logpath.stat().st_size == 0:
        return None
    saw_result_success = False
    saw_result_fail = False
    saw_any = False
    # Match ONLY the structured verdict marker, e.g.  'result': 'success'
    # or "result": "fail"/"failure". Normalize quotes/spaces first so the
    # word "failure" inside a success reason can't trigger a false FAIL.
    succ_re = re.compile(r"""['"]result['"]\s*:\s*['"]success['"]""")
    fail_re = re.compile(r"""['"]result['"]\s*:\s*['"](fail|failure|failed)['"]""")
    for ln in read_lines_safe(logpath):
        saw_any = True
        if succ_re.search(ln):
            saw_result_success = True
        elif fail_re.search(ln):
            saw_result_fail = True
    if saw_result_success:
        return "PASS"
    if saw_result_fail:
        return "FAIL"
    if saw_any:
        return "RAN"
    return None


def parse_gemini_report(category):
    """Return {case_basename: verdict_string} from Dataset/<cat>/test_report.md."""
    report = GEMINI_ROOT / category / "test_report.md"
    verdicts = {}
    if not report.is_file():
        return verdicts
    for ln in read_lines_safe(report):
        # | 3 | FossifyOrg_File-Manager_195 | App | Issue | ✅ PASS (465.4s) | ...
        m = re.match(r"^\|\s*\d+\s*\|\s*([^|]+?)\s*\|.*?\|.*?\|\s*([^|]+?)\s*\|", ln)
        if m:
            case = m.group(1).strip()
            carbon = m.group(2).strip()
            verdicts[case] = carbon
    return verdicts


def base_name(case_folder_name):
    """Strip trailing ' Tested' / ' Tested F' so it matches report case names."""
    n = case_folder_name
    for suffix in (" Tested F", " Tested"):
        if n.endswith(suffix):
            return n[: -len(suffix)]
    return n


def gemini_short(verdict):
    if not verdict:
        return "—"
    if verdict.startswith("*not tested*") or "not tested" in verdict:
        return "not tested"
    if "PASS" in verdict:
        return "✅ PASS"
    if "FAIL" in verdict:
        return "❌ FAIL"
    if "TIMEOUT" in verdict:
        return "⏱ TIMEOUT"
    return verdict


def oa_short(v):
    return {"SUCCESS": "✅", "FAIL-timeout": "❌ timeout",
            "FAIL-loop": "❌ loop", "incomplete": "⚠️ incomplete"}.get(v, v)


rows_by_cat = {}
counts = {"oa_success": 0, "oa_fail": 0, "oa_incomplete": 0,
          "gem_pass": 0, "gem_fail": 0, "gem_ran": 0, "gem_nolog": 0}

for category in CATEGORIES:
    gem_verdicts = parse_gemini_report(category)
    cat_results = RESULTS / category
    if not cat_results.is_dir():
        continue
    rows = []
    for case_dir in sorted(cat_results.iterdir(), key=lambda p: p.name.lower()):
        if not case_dir.is_dir():
            continue
        case = case_dir.name
        logs = sorted(case_dir.glob("*.log"))
        # choose primary OpenAI log: success log > concluded-fail log > largest
        primary = None
        primary_v = "incomplete"
        best_rank = -1
        rank = {"SUCCESS": 3, "FAIL-loop": 2, "FAIL-timeout": 2, "incomplete": 0}
        for lg in logs:
            v = openai_verdict(lg)
            r = rank.get(v, 0)
            # tie-break by size
            score = (r, lg.stat().st_size if lg.exists() else 0)
            if score > (best_rank if isinstance(best_rank, tuple) else (-1, -1)):
                best_rank = score
                primary = lg
                primary_v = v
        # OpenAI cell
        if primary is not None:
            oa_cell = f"[{oa_short(primary_v)}]({rel_link(primary)})"
        else:
            oa_cell = "—"
        # extra OpenAI logs (re-runs)
        extra = [l for l in logs if l != primary]
        if extra:
            extra_links = " ".join(f"[log{i+2}]({rel_link(l)})" for i, l in enumerate(extra))
            oa_cell += f" · {extra_links}"

        # Gemini side — verdict derived from the carbon_log.txt itself, with the
        # category test_report.md used only as a cross-check label.
        gem_case_dir = GEMINI_ROOT / category / case
        gem_log = gem_case_dir / "carbon_log.txt"
        log_verdict = gemini_log_verdict(gem_log)
        report_verdict = gem_verdicts.get(base_name(case), "")

        label_map = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "RAN": "▶ ran (no verdict)"}
        if log_verdict is not None:
            label = label_map[log_verdict]
            gem_cell = f"[{label}]({rel_link(gem_log)})"
        elif "PASS" in report_verdict:
            # report says pass but no per-case log on disk
            gem_cell = "✅ PASS (report)"
        elif report_verdict and "not tested" in report_verdict:
            gem_cell = "not tested"
        else:
            gem_cell = "— (no log)"

        # counts
        if primary_v == "SUCCESS":
            counts["oa_success"] += 1
        elif primary_v.startswith("FAIL"):
            counts["oa_fail"] += 1
        else:
            counts["oa_incomplete"] += 1
        if log_verdict == "PASS" or "PASS" in report_verdict:
            counts["gem_pass"] += 1
        elif log_verdict == "FAIL":
            counts["gem_fail"] += 1
        elif log_verdict == "RAN":
            counts["gem_ran"] += 1
        else:
            counts["gem_nolog"] += 1

        rows.append((case, oa_cell, gem_cell))
    rows_by_cat[category] = rows

# ---- emit markdown ----
out = []
out.append("# CARBON carbon-100 — Per-Case Log Index (OpenAI gpt-4o vs Gemini 2.5 Pro)")
out.append("")
out.append("Click a cell to open that run's raw `.log` file.")
out.append("")
out.append("- **OpenAI gpt-4o** logs: `Dataset/carbon-100/Results/<category>/<case>/<timestamp>.log` (this run). "
           "`log2`/`log3` are automatic re-run attempts for the same case.")
out.append("- **Gemini 2.5 Pro (CARBON)** logs: `Dataset/<category>/<case>/carbon_log.txt` (prior baseline). "
           "The verdict shown is read directly from that log: **✅ PASS** = log emitted `'result': 'success'`, "
           "**❌ FAIL** = emitted a fail result, **▶ ran (no verdict)** = Gemini ran but the log has no explicit "
           "result line, **— (no log)** = no per-case Gemini log on disk.")
out.append("")
out.append(f"OpenAI totals (primary logs): {counts['oa_success']} success · "
           f"{counts['oa_fail']} fail · {counts['oa_incomplete']} incomplete.")
out.append(f"Gemini/CARBON totals (from logs): {counts['gem_pass']} pass · {counts['gem_fail']} fail · "
           f"{counts['gem_ran']} ran-no-verdict · {counts['gem_nolog']} no-log.")
out.append("")

for category in CATEGORIES:
    rows = rows_by_cat.get(category, [])
    if not rows:
        continue
    out.append(f"## {category}  ({len(rows)} cases)")
    out.append("")
    out.append("| Case | OpenAI gpt-4o | Gemini 2.5 Pro (CARBON) |")
    out.append("|---|---|---|")
    for case, oa, gem in rows:
        out.append(f"| {case} | {oa} | {gem} |")
    out.append("")

(REPO / "run_logs_index.md").write_text("\n".join(out), encoding="utf-8")
print("wrote", REPO / "run_logs_index.md")
print("rows:", sum(len(v) for v in rows_by_cat.values()))
print("counts:", counts)
