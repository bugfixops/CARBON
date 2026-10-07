"""Build the audit sheets for the 100-bug capability benchmark: one row per bug
and configuration (CARBON, its three ablations, ReBL), from each run's log.

  python make_audit_sheets.py        # writes <config>_audit.csv beside this file

Columns
  case, category, bug_type        bug and its type (crash bugs per baselines/harness/cases_manifest.json)
  claimed                         the tool's own final verdict in its log ("success", "fail", or "none")
  audited                         the published verdict (the log banner's Status, which equals RESULTS.md)
  actions, duration_s             criteria 2 and 3: actions executed and run length, from the log's end marker
                                  (the last run when a log holds two). A run that ended without one (the
                                  budget ran out) takes its length from the harness's Execution Time line.
                                  Both are blank when the log kept no transcript (seven No-Annotation runs).
  evidence_kind                   criterion 5, for claimed successes:
                                    logcat   a FATAL EXCEPTION or ANR line reported to the LLM during the run
                                    screen   no such line; the claim rests on what the run's screens showed
                                    recording  confirmed on the screen-recorded audit re-run
  evidence                        the logcat line, or the start of the tool's stated reason
  audit_note                      why a claimed success was rejected (from the authors' audit)
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
REPO = BENCH.parents[1]
CONFIGS = {
    "carbon": "carbon_log.txt",
    "carbon_no_annotation": "abalation-tests/carbon_no_annotation_log.txt",
    "carbon_no_screenshot": "abalation-tests/carbon_no_screenshot_log.txt",
    "carbon_no_logcat": "abalation-tests/carbon_no_oracle_log.txt",
    "rebl": "rebl_log.txt",
}
# Audit re-runs with screen recording (Section 4.4 of the paper): five confirmed, two not.
RECORDED = {"FossifyOrg_Gallery_363", "Pool-Of-Tears_GreenStash_170", "FossifyOrg_Camera_91",
            "FossifyOrg_Gallery_289", "msasikanth_twine_1566"}
NOTES = {
    "carbon": {
        "FossifyOrg_File-Manager_195": "Animation-only symptom (icon flicker): not visible in the log, the screenshot, or the screen-recorded re-run.",
        "libre-tube_LibreTube_8245": "Animation-only symptom (back-button lag): not visible in the log, the screenshot, or the screen-recorded re-run.",
        "FossifyOrg_Calendar_1103": "The symptom is what TalkBack announces; the run inferred it from the hierarchy without TalkBack.",
        "ankidroid_Anki-Android_14934": "The symptom is what TalkBack announces; the run inferred it from the hierarchy without TalkBack.",
    },
    "rebl": {
        # success declared after performing the steps, without the symptom being observed
        "TeamNewPipe_NewPipe_8338": "Steps only: the reason says the swipe worked as expected and the bug 'could' occur.",
        "openboard-team_openboard_613": "Steps only: the word 'should be' flagged; no flag was observed.",
        "openboard-team_openboard_758": "Steps only: the reason says navigation worked, contradicting the report.",
        "FossifyOrg_Camera_91": "Steps only: 'the condition for the bug to manifest has been met'.",
        "FossifyOrg_Gallery_289": "Steps only: 'I cannot visually inspect the image content for artifacts'.",
        "FossifyOrg_Paint_125": "Steps only: 'executing these steps is sufficient to consider the bug reproduced'.",
        "ankidroid_Anki-Android_17667": "Steps only: 'by reaching this screen, we have triggered the condition'.",
        "ankidroid_Anki-Android_20789": "Steps only: the reason leaves the triggering step (locking the screen) to the user.",
        "bartoostveen_ViTune_710": "Steps only: the wrong album art 'is expected to occur'; not observed.",
        "libre-tube_LibreTube_8245": "Steps only: 'successfully triggers the conditions'; the lag was not observed.",
        # a symptom is claimed, but the log does not show the reported one
        "FossifyOrg_Gallery_584": "The 'Open with' chooser it cites is not the reported failure to open the image.",
        "LawnchairLauncher_lawnchair_1247": "The 'isn't responding' dialog is not the reported crash, which needs TalkBack's move action.",
        "FossifyOrg_File-Manager_195": "Cites a user confirmation that does not exist; the icon flicker is not visible in the log.",
        "FossifyOrg_Messages_359": "The unchanged hierarchy after one scroll does not show the reported non-scrolling list.",
        "espresso3389_methings_34": "The claimed menu freeze and UI corruption do not appear in the log's screens.",
        "FossifyOrg_Calendar_1103": "The symptom is what TalkBack announces; the run inferred it from the hierarchy without TalkBack.",
    },
}
RESULT = re.compile(r"""['"]result['"]\s*:\s*['"](success|fail)['"]""")
REASON = re.compile(r"""['"]reason['"]\s*:\s*(["'])(.*?)(?<!\\)\1""", re.S)
LOGCAT = re.compile(r">>[^\n]*(FATAL EXCEPTION[^\n']*|ANR in[^\n']*)")


def body(text):
    return text.split("[/LOG-VERDICT-BANNER v1]", 1)[-1].split("FULL EXECUTION LOG", 1)[-1]


def row(case, info, config, path):
    text = path.read_text(errors="replace")
    b = body(text)
    status = re.search(r"^Status : (\w+)", text, re.M)
    results = RESULT.findall(b)
    claimed = results[-1] if results else "none"
    reasons = REASON.findall(b)
    reason = re.sub(r"\s+", " ", reasons[-1][1]).strip() if reasons else ""
    ends = re.findall(r"Execution time: ([\d.]+) seconds", b)
    wall = re.search(r"Execution Time:\s+([\d.]+)\s*s", text)     # the harness's record, kept when the loop logged none
    secs = float(ends[-1]) if ends else float(wall.group(1)) if wall else None
    acts = re.findall(r"Total Commands: (\d+)", b)
    out = {"case": case, "category": info["category"], "bug_type": "crash" if info["crash_bug"] else "non-crash",
           "claimed": claimed, "audited": "pass" if status and status.group(1) == "SUCCESS" else "fail",
           "actions": acts[-1] if acts else "", "duration_s": round(secs) if secs is not None else "",
           "evidence_kind": "", "evidence": "", "audit_note": NOTES.get(config, {}).get(case, "")}
    if claimed == "success" and out["audited"] == "fail" and not out["audit_note"]:
        out["audit_note"] = "Rejected on audit."   # per-case reasons are recorded for CARBON and ReBL only
    if claimed == "success":
        fatal = LOGCAT.search(b)
        if config == "carbon" and case in RECORDED:
            out["evidence_kind"], out["evidence"] = "recording", reason[:300]
        elif fatal:
            out["evidence_kind"], out["evidence"] = "logcat", fatal.group(0).strip()[:300]
        else:
            out["evidence_kind"], out["evidence"] = "screen", reason[:300]
    return out


def main():
    manifest = json.loads((REPO / "baselines/harness/cases_manifest.json").read_text())
    for config, rel in CONFIGS.items():
        rows = []
        for case, info in sorted(manifest.items()):
            hits = sorted(BENCH.glob(f"*/{case}/{rel}"))
            if hits:
                rows.append(row(case, info, config, hits[0]))
        with open(HERE / f"{config}_audit.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        claimed = [r for r in rows if r["claimed"] == "success"]
        crash = [r for r in claimed if r["bug_type"] == "crash" and r["audited"] == "pass"]
        print(f"{config:22s} rows {len(rows):3d}  claimed {len(claimed):3d}  passed {sum(r['audited'] == 'pass' for r in rows):3d}  "
              f"crash passes: logcat {sum(r['evidence_kind'] == 'logcat' for r in crash)}, "
              f"screen {sum(r['evidence_kind'] == 'screen' for r in crash)}")


if __name__ == "__main__":
    main()
