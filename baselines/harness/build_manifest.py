"""Build harness/cases_manifest.json for the 100-bug benchmark.

For every case under results/category-testing-gemini-2.5-pro/<category>/<case>/
it records the category, the APK file name the earlier runs installed (from the
ablation log headers), the package and launch activity (first read from the logs
of an earlier, discarded ReActDroid adaptation, which are no longer kept, and
carried over from the existing manifest), and whether the bug is one of the 17
crash bugs.

The harness re-checks package and activity on the device at run time; this file
is the fallback and the record of what was expected.

Usage:  python harness/build_manifest.py
"""
import glob
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATASET = REPO / "results" / "category-testing-gemini-2.5-pro"

# The 17 crash bugs (Dataset audit used for the paper's 17 crash / 83 non-crash split).
CRASH_BUGS = {
    "FossifyOrg_Calendar_1035", "FossifyOrg_Gallery_584", "LawnchairLauncher_lawnchair_4786",
    "TeamNewPipe_NewPipe_10750", "LawnchairLauncher_lawnchair_1247", "LawnchairLauncher_lawnchair_4320",
    "breezy-weather_breezy-weather_2159", "fcitx5-android_fcitx5-android_841", "Anthonyy232_Paperize_325",
    "Crustack_NotallyX_570", "breezy-weather_breezy-weather_1639", "streetcomplete_StreetComplete_6068",
    "ankidroid_Anki-Android_18529", "Droid-ify_client_238", "FossifyOrg_Notes_190",
    "LawnchairLauncher_lawnchair_5496", "iamrasel_lunar-launcher_82",
}

# The earlier ReActDroid run for this case died before printing its package.
FALLBACK_APP = {"ankidroid_Anki-Android_17667": ("com.ichi2.anki", ".IntentHandler")}


def first_match(pattern, paths):
    for p in paths:
        try:
            m = re.search(pattern, Path(p).read_text(encoding="utf-8", errors="replace"), re.M)
        except OSError:
            continue
        if m:
            return m.group(1).strip()
    return None


def main():
    # APK names and Drive ids from the published archive (harness/index_drive.py).
    # The archive is what the paper distributes, so its file wins when the
    # earlier ablation logs name a different one.
    sources_file = HERE / "apk_sources.json"
    sources = json.loads(sources_file.read_text())["sources"] if sources_file.exists() else {}
    out = HERE / "cases_manifest.json"
    previous = json.loads(out.read_text()) if out.exists() else {}
    cases = {}
    for case_dir in sorted(DATASET.glob("*/*/")):
        category, case = case_dir.parent.name, case_dir.name
        if not (case_dir / "bug_report.txt").is_file():
            continue
        ablation_logs = sorted(glob.glob(str(case_dir / "abalation-tests" / "*.txt")))
        apk = first_match(r"^APK installed:\s*(\S.*?\.apk)\s*$", ablation_logs)
        package = previous.get(case, {}).get("package")
        activity = previous.get(case, {}).get("activity")
        if not package and case in FALLBACK_APP:
            package, activity = FALLBACK_APP[case]
        report = (case_dir / "bug_report.txt").read_text(encoding="utf-8", errors="replace")
        version = re.search(r"^Version:\s*(\S+)", report, re.M)
        src = sources.get(case, {})
        cases[case] = {
            "category": category,
            "bug_report": str((case_dir / "bug_report.txt").relative_to(REPO)),
            "report_version": version.group(1) if version else None,
            "apk": src.get("apk", apk),
            "apk_logged": apk,
            "drive_id": src.get("drive_id"),
            "apk_url": src.get("url"),
            "package": package,
            "activity": activity,
            "crash_bug": case in CRASH_BUGS,
        }
    missing = [c for c in CRASH_BUGS if c not in cases]
    if missing:
        raise SystemExit(f"crash bugs not found in the dataset: {missing}")
    out.write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}: {len(cases)} cases, "
          f"{sum(c['crash_bug'] for c in cases.values())} crash bugs, "
          f"{sum(1 for c in cases.values() if not c['apk'])} without APK name, "
          f"{sum(1 for c in cases.values() if not c['package'])} without package")


if __name__ == "__main__":
    main()
