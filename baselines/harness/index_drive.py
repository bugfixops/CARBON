"""Map every benchmark case to its APK in the public dataset archive on Google Drive.

Writes harness/apk_sources.json: {case: {"drive_id", "drive_path", "apk"}}.
CI downloads each APK by file id, so jobs never have to list the folder.

The archive is the one linked from the root README:
https://drive.google.com/drive/folders/1j81nyTpwsey1_Z1boODJmEtApxFbLs0v

Rule per case: the APK files inside <category>/<case>[ Tested[ F]]/ ; if there
are several, the one at the case folder's top level whose name matches the APK
the earlier runs logged; otherwise the single top-level APK. Any case where the
archive's file name differs from the earlier logs is listed under "notes".

Usage (needs `pip install gdown`):  python harness/index_drive.py
"""
import json
import re
import sys
from pathlib import Path

import gdown

FOLDER = "https://drive.google.com/drive/folders/1j81nyTpwsey1_Z1boODJmEtApxFbLs0v"

# Cases whose archive copy is not the version the bug report names. The file
# comes from the app's own release instead.
OVERRIDES = {
    "FossifyOrg_Gallery_940": {
        "apk": "gallery-26-foss-release.apk",
        "url": "https://github.com/FossifyOrg/Gallery/releases/download/1.12.0/gallery-26-foss-release.apk",
        "drive_id": None, "drive_path": None,
        "note": "archive has gallery-28 (1.13.1); the bug report says 1.12.0 and the earlier ablation runs "
                "installed gallery-26, which is Fossify's 1.12.0 release asset, so that file is used",
    },
}
HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent / "harness"


def case_key(path):
    parts = path.split("/")
    if len(parts) < 3:
        return None
    return parts[0], re.sub(r" Tested( F)?$", "", parts[1])


def main():
    manifest = json.loads((HARNESS / "cases_manifest.json").read_text())
    listing = gdown.download_folder(url=FOLDER, skip_download=True, quiet=True)
    apks = [f for f in listing if f.path.endswith(".apk")]
    sources, notes, missing = {}, {}, []
    for case, info in sorted(manifest.items()):
        logged = info.get("apk_logged") or info["apk"]
        hits = [f for f in apks if case_key(f.path) == (info["category"], case)]
        top = [f for f in hits if len(f.path.split("/")) == 3]
        exact = [f for f in top if f.path.endswith("/" + logged)]
        pick = exact[0] if exact else (top[0] if len(top) == 1 else None)
        if pick is None:
            missing.append((case, [h.path for h in hits]))
            continue
        name = pick.path.rsplit("/", 1)[1]
        sources[case] = {"drive_id": pick.id, "drive_path": pick.path, "apk": name}
        if name != logged:
            notes[case] = f"archive has {name}; the earlier ablation logs installed {logged}"
        elif len(hits) > 1:
            notes[case] = f"{len(hits)} copies in the archive; using {pick.path}"
    for case, o in OVERRIDES.items():
        o = dict(o)
        notes[case] = o.pop("note")
        sources[case] = o
        missing = [m for m in missing if m[0] != case]
    if missing:
        sys.exit(f"no unambiguous APK for: {missing}")
    out = {"archive": FOLDER, "sources": sources, "notes": notes}
    (HARNESS / "apk_sources.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote harness/apk_sources.json: {len(sources)} cases, {len(notes)} notes")
    for case, note in notes.items():
        print(f"  {case}: {note}")


if __name__ == "__main__":
    main()
