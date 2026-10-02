"""
Push the seed-media set (from seed_media_gen.py) onto one or more emulators and
trigger a MediaStore rescan so gallery/player/music/file-manager apps see them.

The framework does NOT provision media on its own, so this must run before the
test batch (run.sh calls it automatically) — or manually any time to (re)load a
device:

    python push_seed_media.py 5554,5556,5558
    python push_seed_media.py            # auto-detect all running emulators

Staged folders under Automation/seed_media/<DEST>/ map to /sdcard/<DEST>/ on the
device (Pictures, DCIM/Camera, Movies, Music, Documents, Download).
"""
import os
import subprocess
import sys
from pathlib import Path

try:
    import adbutils
    ADB = adbutils.adb_path()
except Exception:
    ADB = "adb"

SEED_ROOT = Path(__file__).resolve().parent / "seed_media"

# staging subdir -> on-device path
DEST_MAP = {
    "Pictures": "/sdcard/Pictures",
    "DCIM/Camera": "/sdcard/DCIM/Camera",
    "Movies": "/sdcard/Movies",
    "Music": "/sdcard/Music",
    "Documents": "/sdcard/Documents",
    "Download": "/sdcard/Download",
}


def _adb(serial, *args, timeout=120):
    cmd = [ADB, "-s", serial, *args]
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def detect_devices():
    r = subprocess.run([ADB, "devices"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    ports = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.endswith("\tdevice") and line.startswith("emulator-"):
            ports.append(line.split("\t")[0].replace("emulator-", ""))
    return ports


def push_to_device(port):
    serial = f"emulator-{port}"
    print(f"[seed-push] {serial}: pushing seed media...")
    for sub, dest in DEST_MAP.items():
        src = SEED_ROOT / sub
        if not src.is_dir():
            continue
        # ensure destination exists
        _adb(serial, "shell", "mkdir", "-p", dest)
        # push each file (push the folder contents, preserving nested dirs)
        for f in sorted(src.rglob("*")):
            if f.is_file():
                rel = f.relative_to(src).as_posix()
                remote = f"{dest}/{rel}"
                remote_dir = remote.rsplit("/", 1)[0]
                _adb(serial, "shell", "mkdir", "-p", remote_dir)
                res = _adb(serial, "push", str(f), remote)
                ok = "1 file pushed" in res.stdout or "pushed." in res.stdout or res.returncode == 0
                print(f"[seed-push] {serial}: {rel} -> {remote} {'OK' if ok else 'FAIL: ' + res.stderr.strip()}")

    # Trigger a full MediaStore rescan so apps immediately see the files.
    print(f"[seed-push] {serial}: triggering MediaStore rescan...")
    # Preferred: recursive scan of the whole sdcard
    scan = _adb(serial, "shell", "cmd", "media_scanner", "-scan", "/sdcard")
    if scan.returncode != 0 or "Unknown" in (scan.stdout + scan.stderr):
        # Fallback: broadcast a media-mounted intent for the volume
        _adb(serial, "shell", "am", "broadcast",
             "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
             "-d", "file:///sdcard")
    print(f"[seed-push] {serial}: done.")


def main():
    if not SEED_ROOT.is_dir():
        print(f"[seed-push] ERROR: {SEED_ROOT} not found. Run seed_media_gen.py first.")
        sys.exit(1)

    if len(sys.argv) >= 2 and sys.argv[1].strip():
        ports = [p.strip() for p in sys.argv[1].split(",") if p.strip()]
    else:
        ports = detect_devices()

    if not ports:
        print("[seed-push] No emulators detected.")
        sys.exit(1)

    print(f"[seed-push] Target device ports: {ports}")
    for port in ports:
        push_to_device(port)
    print("[seed-push] All devices provisioned.")


if __name__ == "__main__":
    main()
