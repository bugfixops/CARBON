"""Download one case's APK.

  python harness/fetch_apk.py <case> --out <dir>      ->  <dir>/<case>/<apk>

Sources, in order:
  0. an APK committed beside the case's bug report (used in place, as
     run_baselines.find_apk prefers it; e.g. the extra case from ReBL's benchmark);
  1. apk_url from harness/apk_sources.json, when a case has one;
  2. the dataset archive on Google Drive, by file id (retried with backoff);
  3. if Drive refuses (it throttles repeated automated downloads), the "APK:"
     URL in the case's bug_report.txt: the upstream release file the dataset's
     APKs were originally downloaded from (see carbon/run_retest_groq.py).
Each download is checked to be a real APK (a zip containing
AndroidManifest.xml), and the source used is written next to it as
<apk>.source, which the harness copies into run.json. The harness also checks
the installed version against the bug report on every run.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import gdown

MANIFEST = Path(__file__).resolve().parents[1] / "harness" / "cases_manifest.json"
EXTRA = MANIFEST.with_name("extra_cases.json")


def is_apk(path):
    try:
        with zipfile.ZipFile(path) as z:
            return "AndroidManifest.xml" in z.namelist()
    except (zipfile.BadZipFile, OSError):
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("case")
    p.add_argument("--out", required=True)
    p.add_argument("--attempts", type=int, default=3, help="attempts per source")
    args = p.parse_args()

    info = (json.loads(MANIFEST.read_text()) | json.loads(EXTRA.read_text())["cases"])[args.case]
    repo = MANIFEST.parents[2]
    local = sorted((repo / info["bug_report"]).parent.glob("*.apk"))
    if local and is_apk(local[0]):
        Path(str(local[0]) + ".source").write_text(f"repo:{local[0].relative_to(repo)}\n")
        print(f"in the repository: {local[0].relative_to(repo)}")
        return
    dest = Path(args.out) / args.case / info["apk"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and is_apk(dest):
        print(f"cached: {dest}")
        return
    report = (MANIFEST.parents[2] / info["bug_report"]).read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^APK:\s*(https?://\S+\.apk)\s*$", report, re.M)
    sources = []
    if info.get("apk_url"):
        sources.append(("url", info["apk_url"], args.attempts))
    if info.get("drive_id"):
        sources.append(("drive", info["drive_id"], args.attempts))
    if m and not info.get("apk_url"):
        sources.append(("report-url", m.group(1), 3))
    for kind, ref, attempts in sources:
        for attempt in range(1, attempts + 1):
            try:
                if kind == "drive":
                    gdown.download(id=ref, output=str(dest), quiet=True)
                else:
                    urllib.request.urlretrieve(ref, dest)
            except Exception as e:
                print(f"{kind} attempt {attempt}: {str(e).strip().splitlines()[0][:160]}", file=sys.stderr)
            if dest.exists() and is_apk(dest):
                Path(str(dest) + ".source").write_text(f"{kind}:{ref}\n")
                print(f"downloaded {dest} from {kind} ({dest.stat().st_size / 1e6:.1f} MB)")
                return
            dest.unlink(missing_ok=True)
            time.sleep(min(20 * attempt, 60))
    sys.exit(f"could not download {info['apk']} for {args.case} from any source: {[k for k, _, _ in sources]}")


if __name__ == "__main__":
    main()
