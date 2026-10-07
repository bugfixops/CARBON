"""Run AdbGPT or ReActDroid on the CARBON benchmark with Gemini 2.5 Pro, or
re-run CARBON itself (carbon/reproduction.py, unchanged) for the
run-to-run variance check.

For each case:
  1. prepare the device exactly as CARBON's run_dataset.py did (uninstall,
     install without auto-granted permissions, default launcher if needed,
     launch);
  2. start a logcat capture (all buffers, with PIDs) and a screen recording;
  3. run the tool in its own process with the shared wall-clock budget
     (default 1,800 s) and a per-run LLM spend cap;
  4. save a final screenshot, the recording, the tool's own output, and every
     LLM call's token usage;
  5. write run.json. The verdict is always PENDING_AUDIT: neither tool has an
     oracle for non-crash symptoms, and ReActDroid's crash check accepts a
     crash in any process, so success is decided by the manual audit.

Examples:
  python harness/run_baselines.py --tool adbgpt --dry-run
  python harness/run_baselines.py --tool adbgpt --cases FossifyOrg_Calendar_1035
  python harness/run_baselines.py --tool reactdroid            # the 17 crash bugs
  python harness/run_baselines.py --tool reactdroid --scope all --resume
  python harness/run_baselines.py --tool carbon --cases A-EDev_Flow_27
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_REPO = HERE.parent
REPO = TEST_REPO.parent
sys.path.insert(0, str(TEST_REPO))

from harness import gemini_client  # noqa: E402
from harness.device import Device, ScreenRecorder, child_env, find_adb, parse_crashes  # noqa: E402

UPSTREAM = {
    "adbgpt": {"url": "https://github.com/sidongfeng/AdbGPT", "commit": "ec29b4bd71f0f6469f35ad4f81b429075fb4266b"},
    "reactdroid": {"url": "https://github.com/wuchiuwong/ReActDroid", "commit": "6bde9cdb3bed89a826c6cccde89ad7c19ef4b340"},
    "carbon": {"url": "https://github.com/bugfixops/CARBON", "path": "carbon/", "commit": "see harness.commit"},
}
TOOL_TEMPERATURE = {"adbgpt": 0.2, "reactdroid": 0.0, "carbon": 0.3}  # each tool's own setting
# llm_error (a Gemini call failed even after retries), infra_error (the device
# automation layer failed) and setup_failed are infrastructure failures:
# --resume and CI's "re-run failed jobs" repeat them.
FINAL_STATUSES = {"finished", "error", "timeout", "spend_cap", "loop_abort"}
# CARBON as in the paper's Gemini run: its loop guard (REBL_MAX_REPEAT, added to
# reproduction.py later) never fired in those logs, so it is switched off; and
# my_gpt.py only builds regional Vertex URLs, so it keeps us-central1.
CARBON_ENV = {"REBL_MAX_REPEAT": 10**9, "VERTEX_LOCATION": "us-central1"}


def display_path(path):
    """Path relative to the CARBON repo when inside it, else absolute."""
    try:
        return str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        return str(Path(path).resolve())


def now_iso():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def git_state():
    try:
        commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
                                text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "baselines"],
                                    capture_output=True, text=True).stdout.strip())
        return {"commit": commit, "baselines_dirty": dirty}
    except Exception:
        return {"commit": None, "baselines_dirty": None}


def load_cases():
    """The 100-bug benchmark plus extra_cases.json, whose cases are marked
    `extra` and run only when named with --cases."""
    cases = json.loads((HERE / "cases_manifest.json").read_text(encoding="utf-8"))
    extra = json.loads((HERE / "extra_cases.json").read_text(encoding="utf-8"))["cases"]
    return cases | {c: dict(info, extra=True) for c, info in extra.items()}


def select_cases(manifest, args):
    if args.cases:
        wanted = [c.strip() for c in args.cases.split(",") if c.strip()]
        unknown = [c for c in wanted if c not in manifest]
        if unknown:
            raise SystemExit(f"unknown case(s): {unknown}")
        names = wanted
    else:
        scope = args.scope or ("crash" if args.tool == "reactdroid" else "all")
        names = [c for c, info in sorted(manifest.items())
                 if not info.get("extra")
                 and (scope == "all" or info["crash_bug"])
                 and (not args.category or info["category"] == args.category)]
    if args.limit:
        names = names[:args.limit]
    return names


def find_apk(case, info, apk_root):
    case_dir = REPO / Path(info["bug_report"]).parent
    local = sorted(case_dir.glob("*.apk"))
    if local:
        return local[0]
    if apk_root:
        root = Path(apk_root)
        for candidate in [root / case / info["apk"], root / info["category"] / case / info["apk"], root / info["apk"]]:
            if candidate.is_file():
                return candidate
        hits = sorted(root.rglob(info["apk"]))
        for hit in hits:
            if case in str(hit):
                return hit
        if len(hits) == 1:
            return hits[0]
    return None


def already_done(out_root, tool, case):
    for run_json in (out_root / tool / case).glob("*/run.json"):
        try:
            if json.loads(run_json.read_text())["status"] in FINAL_STATUSES:
                return True
        except Exception:
            continue
    return False


def tool_python(tool, override):
    if override:
        return override
    venv = TEST_REPO / f".venv-{tool}"
    py = venv / "bin" / "python"
    if not py.exists():
        raise SystemExit(f"{py} not found: run baselines/setup.sh first")
    return str(py)


# Where the dataset's title line lost the issue title, ReActDroid's one-sentence
# input uses the title from GitHub. bug_report.txt itself is left unchanged,
# because the other tools received that exact file.
ISSUE_TITLE_FIXES = {
    # dataset title is just "[BUG]"; github.com/Kin69/EasyNotes/issues/356
    "Kin69_EasyNotes_356": "[BUG] Text not saving in split mode",
}


def reactdroid_crash_desc(bug_report_text, mode, case=None):
    """ReActDroid's paper input is a one-sentence crash overview; the first line
    of bug_report.txt is the issue title. --reactdroid-input full passes the
    whole report instead (the same text the other tools receive)."""
    if mode == "full":
        return bug_report_text.strip()
    return ISSUE_TITLE_FIXES.get(case) or bug_report_text.strip().splitlines()[0].strip()


def carbon_usage(token_file, stdout_file):
    """LLM usage of a CARBON run in usage_totals' format, from the token sidecar
    my_gpt.py keeps (REBL_TOKEN_FILE). Its total_tokens is Vertex's
    totalTokenCount, so total - prompt - completion are the thinking tokens,
    which my_gpt's own cost estimate leaves out. Time spent waiting out 429/5xx
    errors is read from my_gpt's log lines."""
    totals = {"calls": 0, "failed_attempts": 0, "failed_calls": 0, "backoff_s": 0,
              "prompt_tokens": 0, "output_tokens": 0, "thought_tokens": 0, "cost_usd": 0.0}
    try:
        t = json.loads(Path(token_file).read_text(encoding="utf-8"))
    except Exception:
        t = {}
    prompt, output = t.get("prompt_tokens", 0) or 0, t.get("completion_tokens", 0) or 0
    thought = max((t.get("total_tokens", 0) or 0) - prompt - output, 0)
    price = gemini_client.PRICES["gemini-2.5-pro"]
    totals.update({"calls": t.get("calls", 0) or 0, "prompt_tokens": prompt, "output_tokens": output,
                   "thought_tokens": thought,
                   "cost_usd": round((prompt * price["in"] + (output + thought) * price["out"]) / 1e6, 4)})
    try:
        out = Path(stdout_file).read_text(encoding="utf-8", errors="replace")
    except Exception:
        out = ""
    totals["failed_attempts"] = len(re.findall(r"^Attempt \d+ failed", out, re.M))
    totals["backoff_s"] = sum(int(w) for w in re.findall(r"(?:backing off|Waiting) (\d+)s", out))
    tail = out[-4000:]
    # A call that failed after all of my_gpt's retries ends the run in a traceback.
    if "Traceback (most recent call last)" in tail and re.search(
            r"HTTPError|RESOURCE_EXHAUSTED|attempts failed|aiplatform\.googleapis", tail):
        totals["failed_calls"] = 1
    return totals


def appium_up(url):
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/status", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def kill_tree(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=15)
    except Exception:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass


def run_case(args, device, case, info, apk, out_root, py, dev_facts):
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    run_dir = out_root / args.tool / case / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "harness.log"

    def log(msg):
        line = f"[{dt.datetime.now().strftime('%H:%M:%S')}] [{args.tool}] [{case}] {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    freeze = TEST_REPO / f".venv-{args.tool}.freeze.txt"
    if freeze.exists():  # exact package versions this run used
        shutil.copy(freeze, run_dir / "pip_freeze.txt")
    bug_text = (REPO / info["bug_report"]).read_text(encoding="utf-8", errors="replace")
    (run_dir / "bug_report.txt").write_text(bug_text, encoding="utf-8")
    usage_file = run_dir / "llm_usage.jsonl"
    token_file = run_dir / "carbon_tokens.json"
    stop_file = run_dir / "STOP"

    def llm_usage():
        if args.tool == "carbon":
            return carbon_usage(token_file, run_dir / "tool_stdout.log")
        return gemini_client.usage_totals(usage_file)
    record = {
        "tool": args.tool, "case": case, "category": info["category"], "crash_bug": info["crash_bug"],
        "model": gemini_client.model_name(), "temperature": TOOL_TEMPERATURE[args.tool],
        "budget_s": args.budget, "spend_cap_usd": args.spend_cap,
        "upstream": UPSTREAM[args.tool], "harness": git_state(), "device": dev_facts,
        "apk": apk.name, "package": info["package"], "verdict": "PENDING_AUDIT",
    }
    source_file = Path(str(apk) + ".source")  # written by harness/fetch_apk.py
    if source_file.exists():
        record["apk_source"] = source_file.read_text().strip()
    if args.tool == "reactdroid":
        record["reactdroid_input"] = args.reactdroid_input

    package = info["package"]
    was_launcher = False
    recorder = None
    logcat_proc = logcat_file = None
    proc = None
    adbgpt_tmp = None
    try:
        # ReActDroid's published install_app uses `adb install -g` (runtime
        # permissions pre-granted); the harness also allows "All files access",
        # which -g does not cover. AdbGPT has no install step, so it gets
        # CARBON's setup (no pre-granted permissions), as CARBON itself does.
        grant = args.tool == "reactdroid"
        record["install_grants_runtime_permissions"] = grant
        was_launcher = device.install_and_launch(apk, package, log, grant_runtime_permissions=grant)
        time.sleep(5)  # a boot-time ANR dialog can surface a few seconds late
        record["closed_anr_dialogs"] = device.close_foreign_anr_dialogs(package, was_launcher, log)
        record["start_foreground"] = device.foreground_package()
        record["start_focused_window"] = device.focused_window()
        activity = device.launch_activity(package) or info["activity"]
        record["activity"] = activity
        # The installed version must be the one the bug report names.
        app_version = device.version_name(package)
        record.update({"app_version": app_version, "report_version": info.get("report_version"),
                       "version_matches_report": bool(app_version and info.get("report_version")
                                                      and info["report_version"].lstrip("v") in app_version)})
        if not record["version_matches_report"]:
            log(f"WARNING: installed {app_version}, bug report says {info.get('report_version')}")
        logcat_proc, logcat_file = device.start_logcat(run_dir / "logcat.txt")
        if args.record:
            recorder = ScreenRecorder(device, run_dir / "recording")
            recorder.start()

        extra = {"BASELINE_USAGE_FILE": usage_file, "BASELINE_STOP_FILE": stop_file,
                 "BASELINE_MODEL": gemini_client.model_name(), "PYTHONPATH": TEST_REPO}
        if args.tool == "adbgpt":
            w, h = dev_facts["screen"]
            # AdbGPT's adb.py puts this path unquoted into `adb pull` shell
            # commands, so it must not contain spaces (the repo path does).
            # Results are moved into run_dir/adbgpt_output afterwards.
            adbgpt_tmp = Path(tempfile.mkdtemp(prefix=f"adbgpt_{device.serial}_"))
            extra.update({"ADBGPT_SAVE_PATH": adbgpt_tmp,
                          "ADBGPT_BUG_REPORT": run_dir / "bug_report.txt",
                          "XML_SCREEN_WIDTH": w, "XML_SCREEN_HEIGHT": h})
            cwd = TEST_REPO / "AdbGPT"
            cmd = [py, "main.py"]
            grace = 0
        elif args.tool == "carbon":
            # run_dataset.py's invocation: reproduction.py <port> <bug report>,
            # with per-run scratch files and the token sidecar.
            (run_dir / "screenshots").mkdir(exist_ok=True)
            extra.update(CARBON_ENV)
            extra.update({"LLM_MODEL": gemini_client.model_name(), "REBL_TARGET_PACKAGE": package,
                          "REBL_TMP_FILE": run_dir / "carbon_tmp", "REBL_SCREENSHOT_DIR": run_dir / "screenshots",
                          "REBL_TOKEN_FILE": token_file})
            record["carbon_env"] = {k: str(v) for k, v in CARBON_ENV.items()}
            cwd = REPO / "carbon"
            cmd = [py, "-u", "reproduction.py", device.serial.rsplit("-", 1)[-1], str(REPO / info["bug_report"])]
            grace = 0
        else:
            code_copy = run_dir / "ReActDroid"
            shutil.copytree(TEST_REPO / "ReActDroid", code_copy,
                            ignore=shutil.ignore_patterns("motivation", "Data", "__pycache__", "*.pyc"))
            crash_info = {"app_pkg": package, "app_acti": activity, "app_name": case,
                          "crash_desc": reactdroid_crash_desc(bug_text, args.reactdroid_input, case)}
            (run_dir / "case.json").write_text(json.dumps(crash_info, indent=2), encoding="utf-8")
            extra.update({"APPIUM_URL": args.appium_url, "ANDROID_PLATFORM_VERSION": dev_facts["android"],
                          "REACTDROID_DEADLINE": time.time() + args.budget,
                          "REACTDROID_BUDGET_S": args.budget})
            cwd = code_copy / "main"
            cmd = [py, "run_case.py", str(run_dir / "case.json")]
            grace = 60  # ReActDroid stops itself at the deadline; this is a backstop

        record["started_at"] = now_iso()
        started = time.time()
        log(f"starting {args.tool} (budget {args.budget}s, spend cap ${args.spend_cap})")
        with open(run_dir / "tool_stdout.log", "w", encoding="utf-8") as out:
            proc = subprocess.Popen(cmd, cwd=cwd, env=child_env(device.adb_path, device.serial, extra),
                                    stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
            status = None
            while proc.poll() is None:
                time.sleep(2)
                elapsed = time.time() - started
                # Time spent waiting out Gemini quota errors does not count
                # against the tool's budget.
                quota_wait = llm_usage()["backoff_s"]
                if elapsed > args.budget + grace + quota_wait:
                    status = "timeout"
                    log(f"budget reached after {elapsed:.0f}s, stopping the tool")
                    stop_file.write_text("time budget reached", encoding="utf-8")
                    kill_tree(proc)
                    break
                if args.spend_cap > 0:
                    spent = llm_usage()["cost_usd"]
                    if spent >= args.spend_cap:
                        status = "spend_cap"
                        log(f"spend cap reached (${spent:.2f}), stopping the tool")
                        stop_file.write_text("spend cap reached", encoding="utf-8")
                        kill_tree(proc)
                        break
        duration = time.time() - started
        # ReActDroid's perform_logcat() leaves an `adb logcat` child running.
        kill_tree(proc)
        stdout = (run_dir / "tool_stdout.log").read_text(encoding="utf-8", errors="replace")
        if status is None:
            if args.tool == "reactdroid" and "[ReActDroid-harness] DEADLINE" in stdout:
                status = "timeout"
            elif args.tool == "carbon" and proc.returncode == 3:
                status = "loop_abort"  # reproduction.py's loop guard (off by default here)
            else:
                status = "finished" if proc.returncode == 0 else "error"
        if status == "error" and re.search(r"uiautomator2\.exceptions\.\w+|adbutils\.errors\.\w+", stdout[-3000:]):
            # The device automation layer failed (e.g. uiautomator2 GatewayError),
            # not the tool's method: an infrastructure failure to re-run.
            log("device automation error (uiautomator2/adbutils); marking infra_error")
            status = "infra_error"
        if llm_usage()["failed_calls"] and status != "spend_cap":
            # A Gemini call failed even after retries. AdbGPT then crashes;
            # ReActDroid silently falls back to a default action. Either way the
            # run is not a valid result for the tool.
            log(f"Gemini call(s) failed after retries; marking llm_error instead of {status}")
            status = "llm_error"
        record.update({"status": status, "returncode": proc.returncode,
                       "ended_at": now_iso(), "duration_s": round(duration, 1)})
        if args.tool == "adbgpt":
            record["tool_claim"] = "replay_finished" if (status == "finished" and "Prcessing time" in stdout) else None
            record["missing_steps_logged"] = stdout.count("There is a MISSING step!")
            record["components_not_found"] = stdout.count("No component found!")
        elif args.tool == "carbon":
            # CARBON's own verdict: the 'result' of its last answer. The paper's
            # outcome is the manual audit of that claim.
            results = re.findall(r"""['"]result['"]\s*:\s*['"]([^'"]+)['"]""", stdout)
            record["tool_claim"] = f"declared_{results[-1].lower()}" if status == "finished" and results else None
            record["repeat_warnings"] = stdout.count("we are repeating the following steps")
        else:
            record["tool_claim"] = "crash_detected" if "[ReActDroid-harness] CRASH_DETECTED" in stdout else None
            record["recoveries"] = stdout.count("[ReActDroid-harness] RECOVER")
        log(f"tool ended: status={status} claim={record['tool_claim']} after {duration:.0f}s")
    except Exception as e:
        record.update({"status": "setup_failed" if proc is None else "error",
                       "error": f"{type(e).__name__}: {e}", "ended_at": now_iso()})
        log(f"{record['status']}: {e}")
        if proc is not None and proc.poll() is None:
            kill_tree(proc)
    finally:
        if proc is not None and proc.poll() is None:
            kill_tree(proc)
        record.setdefault("status", "interrupted")
        if adbgpt_tmp is not None and adbgpt_tmp.exists():
            shutil.move(str(adbgpt_tmp), str(run_dir / "adbgpt_output"))
        try:
            device.screenshot(run_dir / "final.png")
        except Exception as e:
            log(f"final screenshot failed: {e}")
        if recorder:
            record["recording"] = recorder.stop()
        if logcat_proc:
            logcat_proc.terminate()
            logcat_file.close()
            crashes = parse_crashes((run_dir / "logcat.txt").read_text(encoding="utf-8", errors="replace"),
                                    package)
            record["logcat"] = {"app_crash_or_anr": crashes["app_crash_or_anr"],
                                "app_events": crashes["app_events"],
                                "events_total": len(crashes["events"])}
        device.cleanup(package, was_launcher, log)
        record["llm"] = llm_usage()
        (run_dir / "run.json").write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
        append_summary(out_root / args.tool / "runs.csv", record, run_dir)
        log(f"LLM: {record['llm']['calls']} calls, ${record['llm']['cost_usd']:.3f}; wrote {display_path(run_dir)}")
    return record


SUMMARY_FIELDS = ["case", "category", "crash_bug", "status", "tool_claim", "app_crash_or_anr", "duration_s",
                  "llm_calls", "prompt_tokens", "output_tokens", "thought_tokens", "cost_usd", "verdict", "run_dir"]


def append_summary(path, rec, run_dir):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        if new:
            w.writeheader()
        llm = rec.get("llm", {})
        w.writerow({"case": rec["case"], "category": rec["category"], "crash_bug": rec["crash_bug"],
                    "status": rec.get("status"), "tool_claim": rec.get("tool_claim"),
                    "app_crash_or_anr": rec.get("logcat", {}).get("app_crash_or_anr"),
                    "duration_s": rec.get("duration_s"), "llm_calls": llm.get("calls"),
                    "prompt_tokens": llm.get("prompt_tokens"), "output_tokens": llm.get("output_tokens"),
                    "thought_tokens": llm.get("thought_tokens"), "cost_usd": llm.get("cost_usd"),
                    "verdict": rec["verdict"], "run_dir": display_path(run_dir)})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tool", required=True, choices=["adbgpt", "reactdroid", "carbon"])
    p.add_argument("--serial", default=os.environ.get("ANDROID_SERIAL", "emulator-5554"))
    p.add_argument("--cases", help="comma-separated case ids (default: the tool's scope)")
    p.add_argument("--scope", choices=["crash", "all"],
                   help="default: all 100 bugs for AdbGPT and CARBON, the 17 crash bugs for ReActDroid")
    p.add_argument("--category")
    p.add_argument("--limit", type=int)
    p.add_argument("--budget", type=int, default=1800, help="wall-clock seconds per run (paper: 1800)")
    p.add_argument("--spend-cap", type=float, default=3.0, help="USD per run; 0 disables")
    p.add_argument("--apk-root", default=os.environ.get("CARBON_APK_ROOT"),
                   help="folder holding the benchmark APKs (if not inside the case folders)")
    p.add_argument("--out", default=str(TEST_REPO / "results"))
    p.add_argument("--no-record", dest="record", action="store_false", help="skip the screen recording")
    p.add_argument("--resume", action="store_true", help="skip cases that already have a completed run")
    p.add_argument("--reactdroid-input", choices=["title", "full"], default="title",
                   help="crash description given to ReActDroid (paper: one sentence)")
    p.add_argument("--appium-url", default=os.environ.get("APPIUM_URL", "http://127.0.0.1:4723/wd/hub"))
    p.add_argument("--python", help="interpreter for the tool (default: baselines/.venv-<tool>)")
    p.add_argument("--dry-run", action="store_true", help="list cases and APK status; no device or LLM use")
    args = p.parse_args()

    manifest = load_cases()
    names = select_cases(manifest, args)
    out_root = Path(args.out)
    plan = []
    for case in names:
        apk = find_apk(case, manifest[case], args.apk_root)
        skip = args.resume and already_done(out_root, args.tool, case)
        plan.append((case, apk, skip))
    missing = [c for c, apk, _ in plan if apk is None]
    print(f"{args.tool}: {len(plan)} case(s) selected, {sum(s for *_, s in plan)} already done, "
          f"{len(missing)} without an APK")
    if args.dry_run:
        for case, apk, skip in plan:
            print(f"  {'SKIP ' if skip else ''}{case:45s} {apk if apk else 'APK NOT FOUND'}")
        return
    if missing:
        raise SystemExit(f"APK not found for: {', '.join(missing)} (use --apk-root or put each APK in its case folder)")

    adb = find_adb()
    device = Device(args.serial, adb)
    if device.state() != "device":
        raise SystemExit(f"{args.serial} is not online (adb: {adb})")
    dev_facts = {"serial": args.serial, "android": device.android_version(), "api": device.api_level(),
                 "screen": device.screen_size()}
    if args.tool == "reactdroid" and not appium_up(args.appium_url):
        raise SystemExit(f"Appium is not reachable at {args.appium_url}; see baselines/README.md")
    py = tool_python(args.tool, args.python)
    print(f"device {dev_facts}; python {py}")

    for case, apk, skip in plan:
        if skip:
            continue
        run_case(args, device, case, manifest[case], apk, out_root, py, dev_facts)


if __name__ == "__main__":
    main()
