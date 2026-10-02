"""
Groq retest batch runner for the carbon-100 timeout cases.

Re-runs the 53 cases that hit the 15-minute cap in the original gpt-4o run
(Dataset/carbon-100/Results/), this time with a 30-minute cap per case and
Groq as the LLM provider (OpenAI-compatible endpoint).

Honest-logging rules (do not "fix" these):
  * The per-case log header is printed by my_gpt.py from the live config, so it
    always shows the TRUE provider/model, e.g.
    [LLM] Provider: groq | Model: openai/gpt-oss-120b | Vision: False
  * The real timeout (1800s / 30 min) is written into every case log.
  * Results go to Dataset/carbon-100/Results-groq-retest/ -- never into the
    original Dataset/carbon-100/Results/ folder.

LLM failover across multiple Groq accounts:
  * Secrets GROQ_API_KEY_1..GROQ_API_KEY_4 (any number >= 1) are mapped to
    LLM_API_KEY, LLM_API_KEY2, ... for the child processes.
  * my_gpt.py rotates keys mid-run: 401 -> key marked permanently dead,
    429/5xx -> key marked exhausted for the day, honoring Retry-After.
  * Key-exhaustion state is shared across cases via REBL_KEY_STATE_FILE so a
    dead account is not retried by every subsequent case.

Checkpointing:
  * Each case writes " FINAL status=..." as its last log line when
    it concludes (completed / timeout / install_failed / apk_unavailable /
    error). Restarts skip cases that already have a FINAL line -- a dead key
    never causes a completed case to re-run. Disable with REBL_RERUN_ALL=1.

APK acquisition (the repo contains no APK binaries; .gitignore excludes them):
  1. Parse the "APK: <url>" line from the case's bug_report.txt and download it.
  2. Fallback: "APK Tag: <tag>" + "App: <owner>/<repo>" -> GitHub Releases API
     -> first .apk asset -> download it.
  3. Otherwise the case is logged as apk_unavailable (FINAL, checkpointed).

Usage (single device, e.g. inside android-emulator-runner):
    python run_retest_groq.py 5554 --model openai/gpt-oss-120b

Smoke test (1 case):
    python run_retest_groq.py 5554 --case long_press/FossifyOrg_Messages_641

Wave sharding across a 10-job matrix (job N of 10):
    python run_retest_groq.py 5554 --shard 3 --of 10

Environment:
    GROQ_API_KEY_1..N   one key per Groq account (from GitHub secrets; at least 1)
    GROQ_MODEL          overrides --model
"""
import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

try:
    import adbutils
    _ADB_DIR = str(Path(adbutils.adb_path()).parent)
    if _ADB_DIR not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ADB_DIR + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f" Warning: could not resolve bundled adb via adbutils: {e}")

import uiautomator2 as u2
from apkutils3 import APK

AUTOMATION_DIR = Path(__file__).resolve().parent
REPO_ROOT = AUTOMATION_DIR.parent
DATASET_ROOT = REPO_ROOT / "Dataset"
# NEW results folder -- never mix with Dataset/carbon-100/Results/.
RESULTS_DIR = REPO_ROOT / "Dataset" / "carbon-100" / "Results-groq-retest"
WORK_ROOT = AUTOMATION_DIR / "_retest_work"
APK_DIR = WORK_ROOT / "apks"

# Real per-case ceiling: 30 minutes. Logged honestly in every case log.
TIMEOUT_SECONDS = 1800

DEFAULT_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL_SUGGESTION = "qwen/qwen3.8-27b"
GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"

FINAL_MARKER = " FINAL status="

# The 53 timeout cases: (gesture category, exact case folder name).
TIMEOUT_CASES = [
    ("double_tap", "FossifyOrg_Gallery_584 Tested F"),
    ("double_tap", "LawnchairLauncher_lawnchair_4125 Tested"),
    ("double_tap", "LawnchairLauncher_lawnchair_4786 Tested F"),
    ("double_tap", "Pool-Of-Tears_GreenStash_170 Tested"),
    ("double_tap", "TeamNewPipe_NewPipe_10750 Tested"),
    ("double_tap", "ankidroid_Anki-Android_17393 Tested"),
    ("double_tap", "fast4x_RiMusic_1152 Tested"),
    ("double_tap", "openboard-team_openboard_613 Tested"),
    ("drag_and_drop", "FossifyOrg_Launcher_304 Tested"),
    ("drag_and_drop", "FossifyOrg_Notes_59 Tested"),
    ("drag_and_drop", "LawnchairLauncher_lawnchair_1247 Tested F"),
    ("drag_and_drop", "LawnchairLauncher_lawnchair_4320 Tested"),
    ("drag_and_drop", "MetrolistGroup_Metrolist_3227 Tested"),
    ("drag_and_drop", "NeoApplications_Neo-Launcher_130 Tested"),
    ("drag_and_drop", "breezy-weather_breezy-weather_2159 Tested"),
    ("drag_and_drop", "fcitx5-android_fcitx5-android_841 Tested"),
    ("long_press", "Anthonyy232_Paperize_325 Tested"),
    ("long_press", "Crustack_NotallyX_570 Tested"),
    ("long_press", "FossifyOrg_Launcher_198 Tested"),
    ("long_press", "FossifyOrg_Messages_416 Tested"),
    ("long_press", "FossifyOrg_Messages_641 Tested"),
    ("long_press", "breezy-weather_breezy-weather_1639 Tested"),
    ("long_press", "espresso3389_methings_34 Tested"),
    ("orientation", "FossifyOrg_Clock_85 Tested F"),
    ("pinch_zoom", "FossifyOrg_Calendar_621 Tested"),
    ("pinch_zoom", "FossifyOrg_Camera_23 Tested"),
    ("quick_tap", "ankidroid_Anki-Android_19641 Tested"),
    ("quick_tap", "ankidroid_Anki-Android_20789 Tested F"),
    ("quick_tap", "ankidroid_Anki-Android_7138 Tested"),
    ("quick_tap", "yairm210_Unciv_13517 Tested"),
    ("scroll", "Fandroid745_Open-notes_15 Tested"),
    ("swipe", "A-EDev_Flow_27 Tested"),
    ("swipe", "CodeWorksCreativeHub_mLauncher_809 Tested"),
    ("swipe", "Droid-ify_client_238 Tested"),
    ("swipe", "Droid-ify_client_583 Tested"),
    ("swipe", "FossifyOrg_Calendar_1103 Tested"),
    ("swipe", "FossifyOrg_Clock_156 Tested F"),
    ("swipe", "FossifyOrg_Gallery_237 Tested"),
    ("swipe", "FossifyOrg_Gallery_940 Tested"),
    ("swipe", "FossifyOrg_Launcher_66 Tested"),
    ("swipe", "FossifyOrg_Messages_80 Tested"),
    ("swipe", "Kin69_EasyNotes_356 Tested"),
    ("swipe", "LawnchairLauncher_lawnchair_4642 Tested"),
    ("swipe", "LawnchairLauncher_lawnchair_5496 Tested"),
    ("swipe", "anilbeesetti_nextplayer_1127 Tested"),
    ("swipe", "ankidroid_Anki-Android_14934 Tested F"),
    ("swipe", "bartoostveen_ViTune_710 Tested"),
    ("swipe", "breezy-weather_breezy-weather_205 Tested"),
    ("swipe", "breezy-weather_breezy-weather_85 Tested"),
    ("swipe", "dessalines_thumb-key_371 Tested"),
    ("swipe", "iamrasel_lunar-launcher_82 Tested"),
    ("swipe", "libre-tube_LibreTube_8245 Tested"),
    ("swipe", "msasikanth_twine_1566 Tested"),
]

# Failed for a reason OTHER than the 15-min timeout in the original gpt-4o run:
# a harness error (returncode=3221227274, Windows access violation on the
# original PC -- not a model failure, so worth one retest on a fresh emulator).
# The 7 loop-detector trips from the original run were REMOVED from this list
# on explicit user request (2026-09-25): "what failed with loop do not test
# those, those are failures from openai".
EXTRA_FAILED_CASES = [
    ("scroll", "FossifyOrg_File-Manager_136 Tested"),
    # timed out in the original Sept-22 batch but was missing from TIMEOUT_CASES
    ("double_tap", "gsantner_markor_2746 Tested"),
]

_summary_lock = threading.Lock()
_queue_lock = threading.Lock()


class APKUnavailableError(Exception):
    pass


def _read_lines_safe(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line
    except Exception:
        return


def _already_concluded(category, case_folder):
    """True if this case already has a log ending with the FINAL marker.
    Lets restarts / retries skip completed cases instead of re-running them.
    Disable with REBL_RERUN_ALL=1."""
    if os.environ.get("REBL_RERUN_ALL") == "1":
        return False
    case_results = RESULTS_DIR / category / case_folder
    if not case_results.is_dir():
        return False
    for log in case_results.glob("*.log"):
        try:
            # cheap: scan the tail of the file for the marker
            tail = log.read_text(encoding="utf-8", errors="replace")[-2000:]
            if FINAL_MARKER in tail:
                return True
        except Exception:
            continue
    return False


def _norm_case(s):
    """Accept 'cat/case', 'cat/case Tested', with or without trailing ' F'."""
    s = s.strip()
    if s.endswith(" Tested F"):
        return s
    if s.endswith(" Tested"):
        return s
    return s + " Tested"


def resolve_cases(case=None, cases=None, category=None, limit=None, shard=None, of=None,
                 pool=None):
    """Build the ordered case list from CLI filters, skipping concluded ones.

    pool: the (category, folder) universe to select from; defaults to
    TIMEOUT_CASES. Callers that need a wider failed set pass their own pool
    (e.g. the Gemini retest adds EXTRA_FAILED_CASES)."""
    wanted = None
    if cases:
        wanted = {_norm_case(c) for c in cases.split(",") if c.strip()}
    elif case:
        wanted = {_norm_case(case)}
    if wanted:
        # also match the "F"-suffixed folder variant ("X Tested F"): dispatchers
        # may give the bare name and _norm_case only appends " Tested"
        wanted |= {w + " F" for w in wanted
                   if w.endswith(" Tested") and not w.endswith(" Tested F")}

    selected = []
    for cat, folder in (pool if pool is not None else TIMEOUT_CASES):
        key = f"{cat}/{folder}"
        if wanted and key not in wanted and f"{cat}/{folder}" not in wanted:
            # also try without the " Tested" suffix the user may have omitted
            short = f"{cat}/{folder[:-7]}" if folder.endswith(" Tested") else key
            if short not in wanted:
                continue
        if category and cat != category:
            continue
        if _already_concluded(cat, folder):
            print(f" SKIP concluded: {key}")
            continue
        bug_report = DATASET_ROOT / cat / folder / "bug_report.txt"
        if not bug_report.is_file():
            print(f" SKIP {key}: no bug_report.txt")
            continue
        selected.append((cat, folder, bug_report))

    if shard is not None and of:
        selected = [c for i, c in enumerate(selected) if i % of == shard]
        print(f" shard {shard}/{of}: {len(selected)} case(s)")

    if limit:
        selected = selected[:limit]
    return selected


# ── APK acquisition ──────────────────────────────────────────────────────────

def _github_release_apk(owner_repo, tag):
    """Fallback: resolve the first .apk asset of a GitHub release tag."""
    api = f"https://api.github.com/repos/{owner_repo}/releases/tags/{tag}"
    req = urllib.request.Request(api, headers={"Accept": "application/vnd.github+json",
                                              "User-Agent": "rebl-retest"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        raise APKUnavailableError(f"GitHub releases lookup failed for {owner_repo} tag {tag}: {e}")
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".apk"):
            return asset["browser_download_url"], name
    raise APKUnavailableError(f"No .apk asset on {owner_repo} release {tag}")


def _download(url, dest, log_prefix):
    print(f"{log_prefix} downloading APK: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "rebl-retest"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
            total = 0
            while True:
                chunk = r.read(1024 * 256)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
    except Exception as e:
        if dest.exists():
            dest.unlink()
        raise APKUnavailableError(f"APK download failed ({url}): {e}")
    if total < 100_000:
        dest.unlink(missing_ok=True)
        raise APKUnavailableError(f"APK download too small ({total} bytes): {url}")
    with open(dest, "rb") as f:
        if f.read(4) != b"PK\x03\x04":
            dest.unlink(missing_ok=True)
            raise APKUnavailableError(f"Downloaded file is not a ZIP/APK: {url}")
    print(f"{log_prefix} APK saved: {dest} ({total} bytes)")
    return dest


def ensure_apk(category, case_folder, bug_report, log_prefix):
    """Return a local .apk path for the case, downloading it if needed."""
    APK_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", case_folder)
    dest = APK_DIR / f"{category}__{safe_name}.apk"
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"{log_prefix} reusing cached APK: {dest}")
        return dest

    text = bug_report.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^APK:\s*(\S+)", text, re.M)
    if m and m.group(1).startswith("http"):
        return _download(m.group(1), dest, log_prefix)

    m_app = re.search(r"^App:\s*(\S+)", text, re.M)
    m_tag = re.search(r"^APK Tag:\s*(\S+)", text, re.M)
    if m_app and m_tag:
        url, asset = _github_release_apk(m_app.group(1), m_tag.group(1))
        print(f"{log_prefix} resolved release asset: {asset}")
        return _download(url, dest, log_prefix)

    raise APKUnavailableError(
        f"No usable APK for {category}/{case_folder}: bug_report.txt has neither "
        f"a direct 'APK: <url>' line nor an 'APK Tag:' + 'App:' pair.")


# ── Groq model validation ────────────────────────────────────────────────────

def validate_groq_model(model, api_key):
    """Fail fast with a clear message if the model id is not on the account."""
    req = urllib.request.Request(
        GROQ_MODELS_URL,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "rebl-retest"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit(" FATAL: GROQ_API_KEY_1 rejected (401). "
                     "Check the secret value.")
        sys.exit(f" FATAL: Groq /models returned HTTP {e.code}.")
    except Exception as e:
        sys.exit(f" FATAL: could not reach Groq /models: {e}")
    ids = {m.get("id") for m in data.get("data", [])}
    if model in ids:
        print(f" model '{model}' is available on this Groq account.")
        return
    sugg = ""
    if FALLBACK_MODEL_SUGGESTION in ids:
        sugg = (f" Suggested fallback: re-run with --model "
                f"{FALLBACK_MODEL_SUGGESTION} (it IS available).")
    vision = sorted(i for i in ids if "vision" in i.lower())[:10]
    sys.exit(f" FATAL: model '{model}' not found on this Groq account."
             f"{sugg} Vision-capable models visible: {vision}")


# ── install / launch / cleanup (from run_dataset.py) ─────────────────────────

STOCK_LAUNCHER = "com.google.android.apps.nexuslauncher/.NexusLauncherActivity"


def _is_launcher_app(device, package_name):
    try:
        out = device.shell(f"cmd package query-activities -a android.intent.action.MAIN "
                           f"-c android.intent.category.HOME {package_name}").output
        return package_name in (out or "")
    except Exception:
        try:
            out = device.shell(f"dumpsys package {package_name}").output or ""
            return "android.intent.category.HOME" in out
        except Exception:
            return False


def _set_default_launcher(device, package_name, log_prefix):
    try:
        out = device.shell(f"cmd package query-activities -a android.intent.action.MAIN "
                           f"-c android.intent.category.HOME {package_name}").output or ""
        comp = None
        for line in out.splitlines():
            line = line.strip()
            if package_name in line and "/" in line:
                for tok in line.replace(",", " ").split():
                    if tok.startswith(package_name + "/"):
                        comp = tok
                        break
            if comp:
                break
        if not comp:
            comp = f"{package_name}/.LawnchairLauncher"
        device.shell(f"cmd package set-home-activity {comp}")
        print(f"{log_prefix} set default launcher -> {comp}")
        time.sleep(1)
        return comp
    except Exception as e:
        print(f"{log_prefix} Warning: could not set default launcher for {package_name}: {e}")
        return None


def install_and_launch(device, apk_path, log_prefix):
    apk = APK(str(apk_path))
    package_name = apk.package_name
    print(f"{log_prefix} Installing {apk_path.name} (package: {package_name})")
    try:
        device.app_uninstall(package_name)
    except Exception:
        pass
    try:
        device.app_install(str(apk_path))
    except Exception as e:
        print(f"{log_prefix} install via app_install failed ({e}); retrying with adb -d")
        subprocess.run([adbutils.adb_path(), "-s", str(device.serial), "install",
                        "-r", "-d", "-t", str(apk_path)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    time.sleep(2)

    was_launcher = _is_launcher_app(device, package_name)
    if was_launcher:
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


# ── one case ─────────────────────────────────────────────────────────────────

def groq_keys_from_env():
    keys = []
    for i in range(1, 9):
        k = os.environ.get(f"GROQ_API_KEY_{i}", "")
        if k:
            keys.append(k)
    return keys


def run_one_case(device_port, category, case_folder, bug_report, model):
    log_prefix = f"[dev {device_port}]"
    case_results_dir = RESULTS_DIR / category / case_folder
    case_results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_path = case_results_dir / f"{timestamp}.log"

    banner = (f" CASE {category}/{case_folder} | provider=groq | "
              f"model={model} | timeout={TIMEOUT_SECONDS}s (30 min) | device={device_port}")
    print(f"\n{'=' * 80}\n{banner}\n{'=' * 80}")

    def finalize(status, extra=""):
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"\n{FINAL_MARKER}{status}{extra}\n")
        return {"device": device_port, "category": category, "case": case_folder,
                "status": status, "log": str(log_path)}

    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        lf.write(banner + "\n")

    # 1. APK
    try:
        apk_path = ensure_apk(category, case_folder, bug_report, log_prefix)
    except APKUnavailableError as e:
        print(f"{log_prefix} {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f" {e}\n")
        return finalize("apk_unavailable")

    # 2. device install/launch
    device = u2.connect(f"emulator-{device_port}")
    package_name, was_launcher = None, False
    try:
        package_name, was_launcher = install_and_launch(device, apk_path, log_prefix)
    except Exception as e:
        print(f"{log_prefix} FAILED to install/launch {apk_path.name}: {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f" INSTALL_FAILED: {e}\n")
        return finalize("install_failed")

    # 3. child env: Groq provider + multi-key mapping (never log key values)
    keys = groq_keys_from_env()
    dev_work = WORK_ROOT / f"dev_{device_port}"
    (dev_work / "screenshots").mkdir(parents=True, exist_ok=True)
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUTF8"] = "1"
    child_env["REBL_TMP_FILE"] = str(dev_work / "tmp")
    child_env["REBL_SCREENSHOT_DIR"] = str(dev_work / "screenshots")
    token_file = dev_work / "tokens.json"
    if token_file.exists():
        token_file.unlink()
    child_env["REBL_TOKEN_FILE"] = str(token_file)
    # Shared exhaustion state so a dead account is skipped by later cases too.
    child_env["REBL_KEY_STATE_FILE"] = str(WORK_ROOT / "key_state.json")
    child_env["LLM_PROVIDER"] = "groq"
    child_env["LLM_MODEL"] = model
    child_env.pop("LLM_BASE_URL", None)  # use the provider default
    child_env["LLM_API_KEY"] = keys[0]
    for j, k in enumerate(keys[1:], start=2):
        child_env[f"LLM_API_KEY{j}"] = k
    # Scrub any GROQ_API_KEY_* vars from the child's env (defense in depth;
    # the child only needs the mapped LLM_API_KEY* names).
    for i in range(1, 9):
        child_env.pop(f"GROQ_API_KEY_{i}", None)
    print(f"{log_prefix} {len(keys)} Groq account key(s) configured; model={model}")

    cmd = [sys.executable, "-u", "reproduction.py", str(device_port), str(bug_report)]
    print(f"{log_prefix} Log -> {log_path}")
    status = "completed"
    with open(log_path, "a", encoding="utf-8", errors="replace") as log_file:
        try:
            proc = subprocess.run(cmd, cwd=str(AUTOMATION_DIR), stdout=log_file,
                                  stderr=subprocess.STDOUT, env=child_env,
                                  timeout=TIMEOUT_SECONDS)
            if proc.returncode == 3:
                status = "failed(loop)"
            elif proc.returncode != 0:
                status = f"error(returncode={proc.returncode})"
        except subprocess.TimeoutExpired:
            status = "failed(timeout)"
            log_file.write(f"\n FAILED: exceeded {TIMEOUT_SECONDS}s "
                           f"(30 min) time limit, case aborted.\n")

    # token sidecar (Groq is free-tier; cost stays $0.0)
    tokens = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
              "total_tokens": 0, "est_cost_usd": 0.0}
    try:
        if token_file.exists():
            data = json.loads(token_file.read_text(encoding="utf-8"))
            for k in ("calls", "prompt_tokens", "completion_tokens", "total_tokens"):
                tokens[k] = data.get(k, 0) or 0
            tokens["est_cost_usd"] = data.get("est_cost_usd", 0.0) or 0.0
            with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
                lf.write(f"\n token usage: calls={tokens['calls']} "
                         f"prompt={tokens['prompt_tokens']} "
                         f"completion={tokens['completion_tokens']} "
                         f"total={tokens['total_tokens']} est_cost=${tokens['est_cost_usd']}\n")
    except Exception as e:
        print(f"{log_prefix} Warning: could not read token usage: {e}")

    cleanup_app(device, package_name, log_prefix, was_launcher=was_launcher)
    print(f"{log_prefix} CASE DONE: {category}/{case_folder} -> {status} "
          f"| tokens={tokens['total_tokens']}")
    result = finalize(status)
    result["tokens"] = tokens
    return result


STOP_FLAG = AUTOMATION_DIR / "_STOP"


def worker(device_port, case_queue, summary, model):
    while True:
        if STOP_FLAG.exists():
            print(f"[dev {device_port}] STOP flag detected; finishing.")
            return
        with _queue_lock:
            if not case_queue:
                return
            category, case_folder, bug_report = case_queue.pop(0)
        result = run_one_case(device_port, category, case_folder, bug_report, model)
        with _summary_lock:
            summary.append(result)


def main():
    parser = argparse.ArgumentParser(description="Groq retest of the carbon-100 timeout cases (30-min cap)")
    parser.add_argument("devices", help="Comma-separated emulator ports, e.g. 5554")
    parser.add_argument("--model", default=None, help="Groq model id (default: GROQ_MODEL env or built-in default)")
    parser.add_argument("--category", default=None)
    parser.add_argument("--case", default=None, help="Single case: 'category/folder' (suffix ' Tested' optional)")
    parser.add_argument("--cases", default=None, help="Comma-separated 'category/folder' list")
    parser.add_argument("--shard", type=int, default=None, help="This job's shard index (0-based)")
    parser.add_argument("--of", type=int, default=None, help="Total shard count")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    model = args.model or os.environ.get("GROQ_MODEL", "") or DEFAULT_MODEL
    keys = groq_keys_from_env()
    if not keys:
        sys.exit(" FATAL: no Groq keys found. Set GROQ_API_KEY_1 (.._N) in the environment.")
    print(f" provider=groq model={model} timeout={TIMEOUT_SECONDS}s "
          f"({TIMEOUT_SECONDS // 60} min) keys={len(keys)}")

    validate_groq_model(model, keys[0])

    cases = resolve_cases(case=args.case, cases=args.cases, category=args.category,
                          limit=args.limit, shard=args.shard, of=args.of)
    if not cases:
        print(" No matching cases. Nothing to run.")
        return

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    APK_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    device_ports = [p.strip() for p in args.devices.split(",") if p.strip()]
    print(f" {len(cases)} case(s) across {len(device_ports)} device(s): {device_ports}")

    summary = []
    if len(device_ports) == 1:
        worker(device_ports[0], list(cases), summary, model)
    else:
        case_queue = list(cases)
        threads = []
        for port in device_ports:
            t = threading.Thread(target=worker, args=(port, case_queue, summary, model), daemon=False)
            t.start()
            threads.append(t)
            time.sleep(3)
        for t in threads:
            t.join()

    print(f"\n{'=' * 80}\n BATCH SUMMARY ({len(summary)} case(s))\n{'=' * 80}")
    for r in sorted(summary, key=lambda x: (x["category"], x["case"])):
        print(f"  [dev {r['device']}] {r['category']}/{r['case']}: {r['status']}")
    from collections import Counter
    print("\n Status tally:")
    for s, n in Counter(r["status"] for r in summary).most_common():
        print(f"  {s}: {n}")
    grand_calls = sum(r.get("tokens", {}).get("calls", 0) for r in summary)
    grand_total = sum(r.get("tokens", {}).get("total_tokens", 0) for r in summary)
    print(f"\n TOTAL: calls={grand_calls} tokens={grand_total} (Groq free tier: $0.00)")
    try:
        (RESULTS_DIR / "_batch_summary.json").write_text(json.dumps({
            "provider": "groq",
            "model": model,
            "timeout_seconds": TIMEOUT_SECONDS,
            "groq_accounts_configured": len(keys),
            "cases": summary,
            "totals": {"calls": grand_calls, "total_tokens": grand_total, "est_cost_usd": 0.0},
        }, indent=2), encoding="utf-8")
        print(f" Wrote batch summary -> {RESULTS_DIR / '_batch_summary.json'}")
    except Exception as e:
        print(f" Warning: could not write batch summary: {e}")


if __name__ == "__main__":
    main()
