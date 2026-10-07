"""Check that everything the retest needs works before spending on LLM calls.

  python harness/preflight.py --tool adbgpt
  python harness/preflight.py --tool reactdroid --llm     # --llm makes one ~$0.001 call

Checks, in the order they failed or were missing last time:
  * adb is found AND reachable from `sh -c`, the way AdbGPT's os.system calls it
    (the previous run's every command failed with `sh: adb: command not found`);
  * the emulator is online; Android version, API level and screen size;
  * seed media is on the device (same files CARBON had);
  * the APKs for the selected cases are present;
  * the tool's venv imports the patched tool modules;
  * AdbGPT: uiautomator2 can connect to the device;
  * ReActDroid: Appium answers at --appium-url with the UiAutomator2 driver;
  * --llm: one Gemini call through the shared client.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_REPO = HERE.parent
sys.path.insert(0, str(TEST_REPO))
from harness.device import Device, child_env, find_adb  # noqa: E402
from harness.run_baselines import find_apk, load_cases  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""), flush=True)
    return ok


def run_py(py, code, cwd, env):
    r = subprocess.run([py, "-c", code], cwd=cwd, env=env, capture_output=True, text=True, timeout=300)
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())[-400:]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tool", required=True, choices=["adbgpt", "reactdroid"])
    p.add_argument("--serial", default=os.environ.get("ANDROID_SERIAL", "emulator-5554"))
    p.add_argument("--scope", choices=["crash", "all"])
    p.add_argument("--apk-root", default=os.environ.get("CARBON_APK_ROOT"))
    p.add_argument("--appium-url", default=os.environ.get("APPIUM_URL", "http://127.0.0.1:4723/wd/hub"))
    p.add_argument("--llm", action="store_true", help="make one tiny Gemini call")
    args = p.parse_args()

    adb = find_adb()
    if not check("adb found", bool(adb), adb or "install Android platform-tools or set ANDROID_HOME / ADB"):
        sys.exit(1)
    env = child_env(adb, args.serial)
    r = subprocess.run(["sh", "-c", "command -v adb && adb version | head -1"], env=env,
                       capture_output=True, text=True)
    check("adb reachable from sh -c (AdbGPT's os.system)", r.returncode == 0, r.stdout.strip().replace("\n", " | "))

    dev = Device(args.serial, adb)
    online = dev.state() == "device"
    if not check(f"device {args.serial} online", online, "start the emulator (CARBON's run.sh) first"):
        sys.exit(1)
    w, h = dev.screen_size()
    check("device facts", True, f"Android {dev.android_version()} (API {dev.api_level()}), screen {w}x{h}")
    seed = dev.shell("ls /sdcard/Pictures/photo_large_01.jpg /sdcard/Music/song_01.mp3 2>&1")
    check("seed media on device", "No such file" not in seed,
          "missing: run `python3 carbon/push_seed_media.py " + args.serial.replace("emulator-", "") + "`")

    manifest = load_cases()
    scope = args.scope or ("crash" if args.tool == "reactdroid" else "all")
    cases = [c for c, i in manifest.items() if scope == "all" or i["crash_bug"]]
    missing = [c for c in cases if find_apk(c, manifest[c], args.apk_root) is None]
    check(f"APKs for {len(cases)} {scope} cases", not missing,
          f"{len(missing)} missing, e.g. {missing[:3]} (use --apk-root)" if missing else "all found")

    venv = TEST_REPO / (".venv-adbgpt" if args.tool == "adbgpt" else ".venv-reactdroid")
    py = venv / "bin" / "python"
    if not check(f"{venv.name} exists", py.exists(), "run baselines/setup.sh"):
        sys.exit(1)
    py = str(py)
    tool_env = child_env(adb, args.serial, {"PYTHONPATH": TEST_REPO})
    if args.tool == "adbgpt":
        ok, out = run_py(py, "import sys; sys.path.insert(0, 'utils'); import cfgs, config, ChatGPT, extract_step, "
                             "guided_replay, adb; print(cfgs.MODEL, cfgs.TEMPERATURE)",
                         TEST_REPO / "AdbGPT", tool_env)
        check("AdbGPT modules import", ok, out)
        ok, out = run_py(py, "import uiautomator2 as u2, json; d = u2.connect(); "
                             "print(json.dumps({k: d.info.get(k) for k in ('productName', 'sdkInt')}))",
                         TEST_REPO / "AdbGPT", tool_env)
        check("uiautomator2 connects (ANDROID_SERIAL)", ok, out)
    else:
        ok, out = run_py(py, "import sys; sys.path.append('..'); import tool.environment, tool.observe, "
                             "llm.chat, predict_page.predict_crash_page, main.utils; import tiktoken; "
                             "tiktoken.encoding_for_model('gpt-3.5-turbo'); print('ok')",
                         TEST_REPO / "ReActDroid" / "main", tool_env)
        check("ReActDroid modules import", ok, out)
        try:
            with urllib.request.urlopen(args.appium_url.rstrip("/") + "/status", timeout=5) as resp:
                status = json.loads(resp.read().decode())
            check("Appium server", True, f"{args.appium_url} version "
                  f"{status.get('value', {}).get('build', {}).get('version')}")
        except Exception as e:
            check("Appium server", False, f"{args.appium_url}: {e} (start: appium --base-path /wd/hub)")
        drivers = subprocess.run(["appium", "driver", "list", "--installed", "--json"],
                                 capture_output=True, text=True)
        check("Appium UiAutomator2 driver", "uiautomator2" in drivers.stdout,
              "install: appium driver install uiautomator2")

    if args.llm:
        ok, out = run_py(py, "import runpy; runpy.run_module('harness.gemini_client', run_name='__main__')",
                         TEST_REPO, tool_env)
        check("Gemini call", ok, out)

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed" + (f"; fix: {failed}" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
