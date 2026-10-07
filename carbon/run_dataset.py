"""
Batch runner for the gesture-100 dataset.

Loops over every "<app>_<id> Tested" case folder in
results/category-testing-gemini-2.5-pro/<category>/, and for each case:
  1. Installs the case's APK on an emulator
  2. Launches the installed app
  3. Runs reproduction.py against the case's bug_report.txt
  4. Captures full output to
     results/category-testing-gemini-2.5-pro/<category>/<case>/<timestamp>.log
     (per-app folders mirroring the dataset layout, not one flat dump)
  5. Uninstalls the app before moving to the next case

Supports running MULTIPLE emulators in parallel: cases are sharded across the
given devices, one worker thread per device. Each worker isolates the shared
files reproduction.py touches (the 'tmp' hierarchy dump and the 'screenshots'
folder) via the REBL_TMP_FILE / REBL_SCREENSHOT_DIR env vars, so concurrent
runs never collide.

Usage:
    python run_dataset.py <device_port>[,<port2>,...] [--category NAME] [--limit N] [--case NAME]

Examples:
    python run_dataset.py 5554                       # single emulator, all cases
    python run_dataset.py 5554,5556,5558             # 3 emulators in parallel
    python run_dataset.py 5554,5556,5558 --limit 3   # smoke test: 3 cases across 3 devices
    python run_dataset.py 5554 --category swipe      # one category on one device
"""
import argparse
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Make sure a real adb.exe is reachable by bare "adb" for utils.py's
# subprocess.run(['adb', ...]) calls (clear_logcat, get_logcat, check_crash).
# adbutils bundles its own adb.exe; system-wide adb is not required.
try:
    import adbutils
    _ADB_DIR = str(Path(adbutils.adb_path()).parent)
    if _ADB_DIR not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ADB_DIR + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f"[run_dataset] Warning: could not resolve bundled adb via adbutils: {e}")

import uiautomator2 as u2
from apkutils3 import APK

AUTOMATION_DIR = Path(__file__).resolve().parent
REPO_ROOT = AUTOMATION_DIR.parent
DATASET_ROOT = REPO_ROOT / "results" / "category-testing-gemini-2.5-pro"
# Write per-case logs into the main retest-merge results tree.
RESULTS_DIR = REPO_ROOT / "results" / "category-testing-gemini-2.5-pro"
# Per-device isolation scratch space (tmp hierarchy dumps + screenshots).
WORK_ROOT = AUTOMATION_DIR / "_work"

# Gesture-category case folders (flat: category/<case>/bug_report.txt + *.apk).
# ReBL_Failed_Dataset is excluded by default — it has an extra crash/non_crash
# nesting level and is a separate challenge set, not part of the 100-bug corpus.
CATEGORIES = [
    "double_tap", "drag_and_drop", "long_press", "orientation",
    "pinch_zoom", "quick_tap", "scroll", "swipe",
]

# Serialize summary-list appends and work-queue pops from worker threads.
_summary_lock = threading.Lock()
_queue_lock = threading.Lock()


def _already_concluded(category, case_name):
    """True if this case already has a log with a FINAL verdict (a 'result'
    line or a FAILED-timeout marker). Interrupted/partial logs (e.g. a manual
    KeyboardInterrupt) do NOT count, so they get re-run. Lets us resume a batch
    without redoing completed cases. Disable with REBL_RERUN_ALL=1."""
    if os.environ.get("REBL_RERUN_ALL") == "1":
        return False
    case_results = RESULTS_DIR / category / case_name
    if not case_results.is_dir():
        return False
    for log in case_results.glob("*.log"):
        try:
            for line in _read_lines_safe(log):
                if "'result':" in line or "FAILED: exceeded" in line:
                    return True
        except Exception:
            continue
    return False


def _read_lines_safe(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line
    except Exception:
        return


def canonical_case_filter(case_filter):
    """Normalize a user-supplied case filter to a bare case ID: strip a legacy
    ' Tested' / ' Tested F' suffix (for backward-compatible input only; never
    appended), trim whitespace, and validate the result is a plausible bare
    directory name."""
    if not case_filter:
        return case_filter
    name = re.sub(r" Tested(?: F)?$", "", case_filter.strip())
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", name):
        raise ValueError(f"invalid --case value: {case_filter!r} (normalized to {name!r})")
    return name


def discover_cases(category_filter=None, case_filter=None):
    """Return a list of (category, case_dir, bug_report, apk) tuples,
    skipping cases that already concluded in a prior run."""
    cases = []
    skipped_done = 0
    case_filter = canonical_case_filter(case_filter)
    categories = [category_filter] if category_filter else CATEGORIES
    for category in categories:
        cat_path = DATASET_ROOT / category
        if not cat_path.is_dir():
            print(f"[run_dataset] Skipping missing category folder: {category}")
            continue
        for case_dir in sorted(cat_path.iterdir()):
            if not case_dir.is_dir():
                continue
            if case_filter and case_dir.name != case_filter:
                continue
            bug_report = case_dir / "bug_report.txt"
            apks = list(case_dir.glob("*.apk"))
            if not bug_report.is_file():
                print(f"[run_dataset] SKIP {category}/{case_dir.name}: no bug_report.txt")
                continue
            if not apks:
                print(f"[run_dataset] SKIP {category}/{case_dir.name}: no .apk file")
                continue
            if _already_concluded(category, case_dir.name):
                skipped_done += 1
                continue
            cases.append((category, case_dir, bug_report, apks[0]))
    if skipped_done:
        print(f"[run_dataset] Skipping {skipped_done} already-concluded case(s) from prior run(s).")
    return cases


STOCK_LAUNCHER = "com.google.android.apps.nexuslauncher/.NexusLauncherActivity"


def _is_launcher_app(device, package_name):
    """True if the package declares a HOME launcher activity (i.e. it's a launcher)."""
    try:
        out = device.shell(f"cmd package query-activities -a android.intent.action.MAIN "
                           f"-c android.intent.category.HOME {package_name}").output
        return package_name in (out or "")
    except Exception:
        # Fallback: dumpsys the package for a HOME category
        try:
            out = device.shell(f"dumpsys package {package_name}").output or ""
            return "android.intent.category.HOME" in out
        except Exception:
            return False


def _set_default_launcher(device, package_name, log_prefix):
    """Set a launcher app as the default HOME so home-screen gestures reach it.
    Returns the resolved home component if set, else None."""
    try:
        # Find the package's HOME activity component.
        out = device.shell(f"cmd package query-activities -a android.intent.action.MAIN "
                           f"-c android.intent.category.HOME {package_name}").output or ""
        comp = None
        for line in out.splitlines():
            line = line.strip()
            # look for "<pkg>/<activity>" tokens
            if package_name in line and "/" in line:
                for tok in line.replace(",", " ").split():
                    if tok.startswith(package_name + "/"):
                        comp = tok
                        break
            if comp:
                break
        if not comp:
            # common fallback for Lawnchair
            comp = f"{package_name}/.LawnchairLauncher"
        device.shell(f"cmd package set-home-activity {comp}")
        print(f"{log_prefix} set default launcher -> {comp}")
        time.sleep(1)
        return comp
    except Exception as e:
        print(f"{log_prefix} Warning: could not set default launcher for {package_name}: {e}")
        return None


def install_and_launch(device, apk_path, log_prefix):
    """Install apk_path and launch it. Returns (package_name, was_launcher)."""
    apk = APK(str(apk_path))
    package_name = apk.package_name
    print(f"{log_prefix} Installing {apk_path.name} (package: {package_name})")
    # A prior case may have left a NEWER version of the same package installed
    # (e.g. several Fossify apps share a package family / version codes), which
    # makes the dataset's older APK fail with INSTALL_FAILED_VERSION_DOWNGRADE.
    # Proactively uninstall any existing copy first so the exact dataset version
    # installs cleanly. Then install allowing downgrade as a belt-and-suspenders.
    try:
        device.app_uninstall(package_name)
    except Exception:
        pass
    try:
        device.app_install(str(apk_path))
    except Exception as e:
        # Retry via adb with -d (allow version downgrade) if the wrapper failed.
        print(f"{log_prefix} install via app_install failed ({e}); retrying with adb -d")
        subprocess.run([adbutils.adb_path(), "-s", str(device.serial), "install", "-r", "-d", "-t", str(apk_path)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    time.sleep(2)  # let package manager settle before launch

    was_launcher = _is_launcher_app(device, package_name)
    if was_launcher:
        # Launcher apps must actually BE the home launcher, or home-screen
        # gestures (double-tap-to-sleep, etc.) never reach them. Set it default,
        # then press HOME so the device lands on the app under test.
        _set_default_launcher(device, package_name, log_prefix)
        device.shell("input keyevent KEYCODE_HOME")
        time.sleep(2)
    else:
        device.app_start(package_name, use_monkey=True, wait=True)
        time.sleep(2)
    return package_name, was_launcher


def cleanup_app(device, package_name, log_prefix, was_launcher=False):
    if not package_name:
        return
    try:
        # If we made this a launcher, restore the stock launcher FIRST so the
        # device has a valid home when this package is removed.
        if was_launcher:
            try:
                device.shell(f"cmd package set-home-activity {STOCK_LAUNCHER}")
                device.shell("input keyevent KEYCODE_HOME")
                time.sleep(1)
            except Exception as e:
                print(f"{log_prefix} Warning: could not restore stock launcher: {e}")
        device.app_stop(package_name)
        device.app_uninstall(package_name)
    except Exception as e:
        print(f"{log_prefix} Warning: cleanup failed for {package_name}: {e}")


def run_one_case(device_port, category, case_dir, bug_report, apk_path):
    log_prefix = f"[dev {device_port}]"
    # Mirror the dataset layout: Results/<category>/<case>/<timestamp>.log
    # so each app's logs live in their own folder instead of one flat dump.
    case_results_dir = RESULTS_DIR / category / case_dir.name
    case_results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_path = case_results_dir / f"{timestamp}.log"

    device = u2.connect(f"emulator-{device_port}")
    package_name = None
    print(f"\n{'=' * 80}\n{log_prefix} CASE: {category}/{case_dir.name}\n{'=' * 80}")

    was_launcher = False
    try:
        package_name, was_launcher = install_and_launch(device, apk_path, log_prefix)
    except Exception as e:
        print(f"{log_prefix} FAILED to install/launch {apk_path.name}: {e}")
        log_path.write_text(f"INSTALL_FAILED: {e}\n", encoding="utf-8")
        return {"device": device_port, "category": category, "case": case_dir.name,
                "status": "install_failed", "log": str(log_path)}

    # Per-device isolation: unique scratch dir so the shared 'tmp' hierarchy
    # file and 'screenshots' folder never collide between parallel workers.
    dev_work = WORK_ROOT / f"dev_{device_port}"
    (dev_work / "screenshots").mkdir(parents=True, exist_ok=True)

    child_env = os.environ.copy()
    # Force UTF-8 for the child's stdout/stderr (Windows defaults to cp1252,
    # which crashes on non-ASCII UI text like narrow no-break spaces / emoji).
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUTF8"] = "1"
    # Per-device scratch paths read by hierarchy.py and ui_viewer.py.
    child_env["REBL_TMP_FILE"] = str(dev_work / "tmp")
    child_env["REBL_SCREENSHOT_DIR"] = str(dev_work / "screenshots")
    # Per-case token-usage sidecar (survives even if the case times out).
    token_file = dev_work / "tokens.json"
    if token_file.exists():
        token_file.unlink()
    child_env["REBL_TOKEN_FILE"] = str(token_file)

    cmd = [sys.executable, "-u", "reproduction.py", str(device_port), str(bug_report)]
    print(f"{log_prefix} Running: reproduction.py {device_port} <bug_report>")
    print(f"{log_prefix} Log -> {log_path}")

    status = "completed"
    with open(log_path, "w", encoding="utf-8", errors="replace") as log_file:
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(AUTOMATION_DIR),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env=child_env,
                timeout=900,  # 15-min ceiling per case; exceeding = failed
            )
            if proc.returncode == 3:
                status = "failed(loop)"      # aborted: agent stuck repeating steps
            elif proc.returncode != 0:
                status = f"error(returncode={proc.returncode})"
        except subprocess.TimeoutExpired:
            status = "failed(timeout)"
            log_file.write("\n[run_dataset] FAILED: exceeded 900s (15 min) time limit, case aborted.\n")

    # Read token usage sidecar (present even if the case timed out).
    tokens = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
              "total_tokens": 0, "est_cost_usd": 0.0}
    try:
        if token_file.exists():
            import json as _json
            data = _json.loads(token_file.read_text(encoding="utf-8"))
            for k in ("calls", "prompt_tokens", "completion_tokens", "total_tokens"):
                tokens[k] = data.get(k, 0) or 0
            tokens["est_cost_usd"] = data.get("est_cost_usd", 0.0) or 0.0
            # Ensure the token summary is in the case log even on timeout.
            with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
                lf.write(f"\n[run_dataset] token usage: calls={tokens['calls']} "
                         f"prompt={tokens['prompt_tokens']} completion={tokens['completion_tokens']} "
                         f"total={tokens['total_tokens']} est_cost=${tokens['est_cost_usd']}\n")
    except Exception as e:
        print(f"{log_prefix} Warning: could not read token usage: {e}")

    cleanup_app(device, package_name, log_prefix, was_launcher=was_launcher)
    print(f"{log_prefix} CASE DONE: {category}/{case_dir.name} -> {status} "
          f"| tokens={tokens['total_tokens']} est_cost=${tokens['est_cost_usd']}")
    return {"device": device_port, "category": category, "case": case_dir.name,
            "status": status, "log": str(log_path), "tokens": tokens}


# Graceful-stop flag file. If this exists, workers finish their CURRENT case
# then stop pulling new ones (clean shutdown, no half-written logs).
STOP_FLAG = AUTOMATION_DIR / "_STOP"


def worker(device_port, case_queue, summary):
    """Pull cases off the shared queue and run them on this device until empty
    (or until a graceful-stop flag file appears)."""
    while True:
        if STOP_FLAG.exists():
            print(f"[dev {device_port}] STOP flag detected; finishing (no new case pulled).")
            return
        with _queue_lock:
            if not case_queue:
                return  # queue empty
            category, case_dir, bug_report, apk_path = case_queue.pop(0)
        result = run_one_case(device_port, category, case_dir, bug_report, apk_path)
        with _summary_lock:
            summary.append(result)


def main():
    parser = argparse.ArgumentParser(description="Batch-run the gesture-100 dataset against reproduction.py")
    parser.add_argument("devices", help="Comma-separated emulator ports, e.g. 5554 or 5554,5556,5558")
    parser.add_argument("--category", default=None, help="Only run this gesture category")
    parser.add_argument("--case", default=None, help="Only run this specific case folder name")
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N discovered cases")
    args = parser.parse_args()

    device_ports = [p.strip() for p in args.devices.split(",") if p.strip()]
    if not device_ports:
        print("[run_dataset] No device ports given.")
        return

    cases = discover_cases(category_filter=args.category, case_filter=args.case)
    if args.limit:
        cases = cases[: args.limit]

    if not cases:
        print("[run_dataset] No matching cases found. Nothing to run.")
        return

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[run_dataset] {len(cases)} case(s) across {len(device_ports)} device(s): {device_ports}")

    summary = []

    if len(device_ports) == 1:
        # Single device: run sequentially in the main thread.
        worker(device_ports[0], list(cases), summary)
    else:
        # Multiple devices: shared work queue, one worker thread per device.
        # Threads pull the next case whenever they finish, so faster devices
        # naturally do more work (better load balancing than static sharding).
        case_queue = list(cases)
        threads = []
        for port in device_ports:
            t = threading.Thread(target=worker, args=(port, case_queue, summary), daemon=False)
            t.start()
            threads.append(t)
            time.sleep(3)  # stagger startups so installs don't all hit adb at once
        for t in threads:
            t.join()

    print(f"\n{'=' * 80}\n[run_dataset] BATCH SUMMARY ({len(summary)} case(s))\n{'=' * 80}")
    for r in sorted(summary, key=lambda x: (x["category"], x["case"])):
        tk = r.get("tokens", {})
        print(f"  [dev {r['device']}] {r['category']}/{r['case']}: {r['status']} "
              f"| tokens={tk.get('total_tokens', 0)} est_cost=${tk.get('est_cost_usd', 0.0)}")
    # Status tally
    from collections import Counter
    tally = Counter(r["status"] for r in summary)
    print("\n[run_dataset] Status tally:")
    for status, count in tally.most_common():
        print(f"  {status}: {count}")
    # Grand total tokens + cost across the whole batch.
    grand_calls = sum(r.get("tokens", {}).get("calls", 0) for r in summary)
    grand_prompt = sum(r.get("tokens", {}).get("prompt_tokens", 0) for r in summary)
    grand_completion = sum(r.get("tokens", {}).get("completion_tokens", 0) for r in summary)
    grand_total = sum(r.get("tokens", {}).get("total_tokens", 0) for r in summary)
    grand_cost = round(sum(r.get("tokens", {}).get("est_cost_usd", 0.0) for r in summary), 4)
    print(f"\n[run_dataset] TOTAL TOKENS: calls={grand_calls} prompt={grand_prompt} "
          f"completion={grand_completion} total={grand_total}")
    print(f"[run_dataset] TOTAL ESTIMATED COST: ${grand_cost}")
    # Persist a machine-readable batch summary next to the results.
    try:
        summary_path = RESULTS_DIR / "_batch_summary.json"
        import json as _json
        summary_path.write_text(_json.dumps({
            "cases": summary,
            "totals": {"calls": grand_calls, "prompt_tokens": grand_prompt,
                       "completion_tokens": grand_completion, "total_tokens": grand_total,
                       "est_cost_usd": grand_cost},
        }, indent=2), encoding="utf-8")
        print(f"[run_dataset] Wrote batch summary -> {summary_path}")
    except Exception as e:
        print(f"[run_dataset] Warning: could not write batch summary: {e}")


if __name__ == "__main__":
    main()
