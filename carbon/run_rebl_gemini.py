"""
CARBON over ReBL's benchmark with Gemini (Vertex AI via ADC).

Runs the CARBON bug-reproduction tool over the 95 testable cases in
results/ReBL_Full_Dataset/ (crawled from the ReBL paper's bug-report index),
using gemini-2.5-pro through Vertex AI authenticated with Application
Default Credentials (service-account Bearer token). No API key exists in
this flow: my_gpt.py mints a short-lived OAuth2 token from the
service-account JSON at GOOGLE_APPLICATION_CREDENTIALS.

Layout differences vs the gesture-100 retest driver:
  * Cases live in results/ReBL_Full_Dataset/<crash|non_crash>/<owner_repo_issue>/
    (no gesture categories). Category is "crash" / "non-crash" from
    rebl_cases.json.
  * APKs are LOCAL (<case>/<apk>, recorded in rebl_cases.json) -- no
    download, no bug_report.txt URL parsing.
  * New runs go to carbon/Results/rebl/<crash|non-crash>/<case>/ (git-ignored),
    never into the published results/.

Honest-logging rules (do not "fix" these):
  * The per-case log header is printed by my_gpt.py from the live config, so it
    always shows the TRUE provider/model, e.g.
    [LLM] Provider: vertex-adc | Model: gemini-2.5-pro | Vision: True
  * The real timeout (default 1800s / 30 min, overridable via GEMINI_TIMEOUT_SECONDS)
    is written into every case log.
  * Vertex AI bills GCP credits: per-case token sidecars carry the real
    est_cost_usd computed from the API's usageMetadata.

Usage (single device):
    python run_rebl_gemini.py 5554 --model gemini-2.5-pro

Smoke test (1 case):
    python run_rebl_gemini.py 5554 --case crash/ramack_ActivityDiary_285

Sharding across 10 parallel jobs (job N of 10):
    python run_rebl_gemini.py 5554 --shard 3 --of 10

Environment:
    GOOGLE_APPLICATION_CREDENTIALS   path to the service-account JSON
    GCP_PROJECT_ID                   optional override (else read from the JSON)
    VERTEX_LOCATION                  optional override (default us-central1)
    GEMINI_MODEL                     overrides --model
    GEMINI_MAX_SPEND_USD             per-job spend cap (default 8.00); the job aborts
                                     remaining cases once cumulative est_cost_usd hits it
    REBL_RERUN_ALL=1                 re-run cases that already have committed results
"""
import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import run_retest_groq as base  # shared: install/launch/checkpoint/u2 machinery

AUTOMATION_DIR = base.AUTOMATION_DIR
REPO_ROOT = base.REPO_ROOT
TIMEOUT_SECONDS = int(os.environ.get("GEMINI_TIMEOUT_SECONDS", base.TIMEOUT_SECONDS))
FINAL_MARKER = base.FINAL_MARKER
WORK_ROOT = base.WORK_ROOT

REBL_ROOT = REPO_ROOT / "results" / "ReBL_Full_Dataset"
CASES_FILE = AUTOMATION_DIR / "rebl_cases.json"

# New runs go to a git-ignored folder, never into the published results/.
RESULTS_DIR = AUTOMATION_DIR / "Results" / "rebl"

PROVIDER_NAME = "vertex-adc"
DEFAULT_MODEL = "gemini-2.5-pro"

# Hard spend guardrail: abort remaining cases once the cumulative estimated
# Vertex AI cost for THIS job reaches the cap. Each wave shard enforces its own
# cap, so the worst-case wave total is MAX_SPEND_USD * shard-count.
# Override per run via GEMINI_MAX_SPEND_USD.
MAX_SPEND_USD = float(os.environ.get("GEMINI_MAX_SPEND_USD", "8.00"))
_SPEND_LOCK = threading.Lock()
_SPEND_USD = 0.0
_SPEND_EXCEEDED = threading.Event()


def _load_cases():
    with open(CASES_FILE, encoding="utf-8") as f:
        return json.load(f)["cases"]


def _already_concluded(category, case_folder):
    """True if this case already has a log ending with the FINAL marker.
    Disable with REBL_RERUN_ALL=1."""
    if os.environ.get("REBL_RERUN_ALL") == "1":
        return False
    case_results = RESULTS_DIR / category / case_folder
    if not case_results.is_dir():
        return False
    for log in case_results.glob("*.log"):
        try:
            tail = log.read_text(encoding="utf-8", errors="replace")[-2000:]
            if FINAL_MARKER in tail:
                return True
        except Exception:
            continue
    return False


def resolve_rebl_cases(case=None, cases=None, category=None, limit=None,
                       shard=None, of=None):
    """Build the ordered case list from CLI filters, skipping concluded ones."""
    wanted = None
    if cases:
        wanted = {c.strip() for c in cases.split(",") if c.strip()}
    elif case:
        wanted = {case.strip()}

    selected = []
    for entry in _load_cases():
        cat, folder = entry["category"], entry["folder"]
        key = f"{cat}/{folder}"
        if wanted and key not in wanted and folder not in wanted:
            continue
        if category and cat != category:
            continue
        if _already_concluded(cat, folder):
            print(f"[run_rebl] SKIP concluded: {key}")
            continue
        case_dir = REBL_ROOT / cat.replace("-", "_") / folder
        bug_report = case_dir / "bug_report.txt"
        if not bug_report.is_file():
            print(f"[run_rebl] SKIP {key}: no bug_report.txt")
            continue
        apk_path = case_dir / entry["apk"]
        if not apk_path.is_file():
            print(f"[run_rebl] SKIP {key}: missing APK {entry['apk']}")
            continue
        selected.append((cat, folder, bug_report, apk_path))

    if shard is not None and of:
        selected = [c for i, c in enumerate(selected) if i % of == shard]
        print(f"[run_rebl] shard {shard}/{of}: {len(selected)} case(s)")

    if limit:
        selected = selected[:limit]
    return selected


def ensure_apk_local(category, case_folder, apk_path, log_prefix):
    """The ReBL dataset ships the APK in the case folder -- validate, don't download."""
    size = apk_path.stat().st_size
    if size < 10_000:
        raise base.APKUnavailableError(f"APK too small ({size} bytes): {apk_path}")
    with open(apk_path, "rb") as f:
        if f.read(4) != b"PK\x03\x04":
            raise base.APKUnavailableError(f"Not a ZIP/APK: {apk_path}")
    print(f"{log_prefix} local APK OK: {apk_path.name} ({size} bytes)")
    return apk_path


def _adc_ok():
    p = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    return bool(p and Path(p).is_file())


def ensure_apk_override(path_str, log_prefix):
    """Retest path: use a caller-supplied APK (e.g. the pre-fix version)."""
    p = Path(path_str)
    if not p.is_file():
        raise base.APKUnavailableError(f"override APK not found: {path_str}")
    size = p.stat().st_size
    if size < 100_000:
        raise base.APKUnavailableError(f"override APK too small ({size} bytes): {p.name}")
    with open(p, "rb") as f:
        if f.read(4) != b"PK\x03\x04":
            raise base.APKUnavailableError(f"Not a ZIP/APK: {p.name}")
    print(f"{log_prefix} override APK OK: {p.name} ({size} bytes)")
    return p


def run_one_case(device_port, category, case_folder, bug_report, apk_path, model):
    """One case with the Gemini/Vertex-ADC child env (otherwise shared logic)."""
    log_prefix = f"[dev {device_port}]"
    case_results_dir = RESULTS_DIR / category / case_folder
    case_results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_path = case_results_dir / f"{timestamp}.log"

    banner = (f"[run_rebl] CASE {category}/{case_folder} | provider={PROVIDER_NAME} | "
              f"model={model} | timeout={TIMEOUT_SECONDS}s ({TIMEOUT_SECONDS // 60} min) | device={device_port}")
    print(f"\n{'=' * 80}\n{banner}\n{'=' * 80}")

    def finalize(status, extra=""):
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"\n{FINAL_MARKER}{status}{extra}\n")
        return {"device": device_port, "category": category, "case": case_folder,
                "status": status, "log": str(log_path)}

    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        lf.write(banner + "\n")

    # 1. APK (local to the dataset; REBL_APK_OVERRIDE wins for retests)
    apk_override = os.environ.get("REBL_APK_OVERRIDE", "").strip()
    try:
        if apk_override:
            apk_local = ensure_apk_override(apk_override, log_prefix)
        else:
            apk_local = ensure_apk_local(category, case_folder, apk_path, log_prefix)
    except base.APKUnavailableError as e:
        print(f"{log_prefix} {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"[run_rebl] {e}\n")
        return finalize("apk_unavailable")

    # 2. device install/launch (shared)
    device = base.u2.connect(f"emulator-{device_port}")
    package_name, was_launcher = None, False
    try:
        package_name, was_launcher = base.install_and_launch(device, apk_local, log_prefix)
    except Exception as e:
        print(f"{log_prefix} FAILED to install/launch {apk_local.name}: {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"[run_rebl] INSTALL_FAILED: {e}\n")
        return finalize("install_failed")

    # 2b. optional pre-setup shell (retests): runs after install, before the
    # agent starts. Gets REBL_DEVICE_SERIAL / ANDROID_SERIAL=emulator-<port>.
    pre_setup = os.environ.get("REBL_PRE_SETUP", "").strip()
    if pre_setup:
        penv = os.environ.copy()
        penv["REBL_DEVICE_SERIAL"] = f"emulator-{device_port}"
        penv["ANDROID_SERIAL"] = f"emulator-{device_port}"
        print(f"{log_prefix} running REBL_PRE_SETUP ...")
        try:
            r = subprocess.run(pre_setup, shell=True, cwd=str(AUTOMATION_DIR),
                               env=penv, capture_output=True, text=True, timeout=300)
            with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
                lf.write(f"\n[run_rebl] PRE_SETUP rc={r.returncode}\n{r.stdout}\n{r.stderr}\n")
        except Exception as e:
            with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
                lf.write(f"\n[run_rebl] PRE_SETUP failed: {e}\n")

    # 3. child env: Vertex-ADC provider. The child only ever sees the
    # credentials FILE path -- never the raw GCP_SA_JSON secret.
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
    child_env["LLM_PROVIDER"] = PROVIDER_NAME
    child_env["LLM_MODEL"] = model
    if package_name:
        child_env["REBL_TARGET_PACKAGE"] = package_name
    child_env.pop("LLM_BASE_URL", None)  # use the provider default
    # Scrub key material that must not cross the process boundary.
    child_env.pop("GCP_SA_JSON", None)
    child_env.pop("LLM_API_KEY", None)
    for i in range(2, 20):
        child_env.pop(f"LLM_API_KEY{i}", None)
    print(f"{log_prefix} ADC auth via {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}; model={model}")

    # Agent hint (retests): prepend extra instructions to the bug report the
    # agent sees as its first prompt. Lets a retest correct a previous run's
    # mistake (e.g. "the vault password you set is 1234 -- reuse it").
    hint = os.environ.get("REBL_AGENT_HINT", "").strip()
    report_arg = bug_report
    if hint:
        hinted = dev_work / "bug_report_hinted.txt"
        hinted.write_text(
            hint.rstrip() + "\n\n" + Path(bug_report).read_text(encoding="utf-8", errors="replace"),
            encoding="utf-8")
        report_arg = hinted
        print(f"{log_prefix} agent hint injected ({len(hint)} chars)")

    cmd = [sys.executable, "-u", "reproduction.py", str(device_port), str(report_arg)]
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
            log_file.write(f"\n[run_rebl] FAILED: exceeded {TIMEOUT_SECONDS}s "
                           f"({TIMEOUT_SECONDS // 60} min) time limit, case aborted.\n")

    # token sidecar (Vertex AI bills: est_cost_usd comes from usageMetadata)
    tokens = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
              "total_tokens": 0, "est_cost_usd": 0.0}
    try:
        if token_file.exists():
            data = json.loads(token_file.read_text(encoding="utf-8"))
            for k in ("calls", "prompt_tokens", "completion_tokens", "total_tokens"):
                tokens[k] = data.get(k, 0) or 0
            tokens["est_cost_usd"] = data.get("est_cost_usd", 0.0) or 0.0
            with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
                lf.write(f"\n[run_rebl] token usage: calls={tokens['calls']} "
                         f"prompt={tokens['prompt_tokens']} "
                         f"completion={tokens['completion_tokens']} "
                         f"total={tokens['total_tokens']} est_cost=${tokens['est_cost_usd']}\n")
    except Exception as e:
        print(f"{log_prefix} Warning: could not read token usage: {e}")

    base.cleanup_app(device, package_name, log_prefix, was_launcher=was_launcher)
    print(f"{log_prefix} CASE DONE: {category}/{case_folder} -> {status} "
          f"| tokens={tokens['total_tokens']}")
    result = finalize(status)
    result["tokens"] = tokens
    return result


def worker(device_port, case_queue, summary, model):
    global _SPEND_USD
    while True:
        if base.STOP_FLAG.exists() or _SPEND_EXCEEDED.is_set():
            if _SPEND_EXCEEDED.is_set():
                print(f"[dev {device_port}] Spend cap hit; stopping, no new cases.")
            else:
                print(f"[dev {device_port}] STOP flag detected; finishing.")
            return
        with base._queue_lock:
            if not case_queue:
                return
            category, case_folder, bug_report, apk_path = case_queue.pop(0)
        result = run_one_case(device_port, category, case_folder, bug_report, apk_path, model)
        cost = float(result.get("tokens", {}).get("est_cost_usd", 0.0) or 0.0)
        with _SPEND_LOCK:
            _SPEND_USD += cost
            spent = _SPEND_USD
        print(f"[dev {device_port}] spend so far: ${spent:.4f} / cap ${MAX_SPEND_USD:.2f}")
        if spent >= MAX_SPEND_USD and not _SPEND_EXCEEDED.is_set():
            _SPEND_EXCEEDED.set()
            print(f"[dev {device_port}] *** SPEND CAP REACHED "
                  f"(${spent:.4f} >= ${MAX_SPEND_USD:.2f}); remaining cases aborted. ***")
        with base._summary_lock:
            summary.append(result)


def main():
    parser = argparse.ArgumentParser(
        description="CARBON bug-reproduction over the ReBL dataset with Gemini 2.5 Pro (Vertex AI ADC)")
    parser.add_argument("devices", help="Comma-separated emulator ports, e.g. 5554")
    parser.add_argument("--model", default=None,
                        help="Vertex AI model id (default: GEMINI_MODEL env or gemini-2.5-pro)")
    parser.add_argument("--category", default=None, help="crash | non-crash")
    parser.add_argument("--case", default=None, help="Single case: 'category/folder' or 'folder'")
    parser.add_argument("--cases", default=None, help="Comma-separated case list")
    parser.add_argument("--shard", type=int, default=None, help="This job's shard index (0-based)")
    parser.add_argument("--of", type=int, default=None, help="Total shard count")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    model = args.model or os.environ.get("GEMINI_MODEL", "") or DEFAULT_MODEL
    if not _adc_ok():
        sys.exit("[run_rebl] FATAL: GOOGLE_APPLICATION_CREDENTIALS is not set to an "
                 "existing service-account JSON file.")
    # Fail fast (no billable call): minting a token catches a bad SA file now,
    # not 5 minutes into the first case.
    try:
        import google.auth
        from google.auth.transport.requests import Request as _GARequest
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(_GARequest())
    except Exception as e:
        sys.exit(f"[run_rebl] FATAL: could not mint ADC access token: {e}")
    print(f"[run_rebl] provider={PROVIDER_NAME} model={model} timeout={TIMEOUT_SECONDS}s "
          f"({TIMEOUT_SECONDS // 60} min) ADC token minted OK")
    print(f"[run_rebl] spend cap: ${MAX_SPEND_USD:.2f} per job "
          f"(GEMINI_MAX_SPEND_USD); wave ceiling = cap x shard count")

    cases = resolve_rebl_cases(case=args.case, cases=args.cases, category=args.category,
                               limit=args.limit, shard=args.shard, of=args.of)
    if not cases:
        print("[run_rebl] No matching cases. Nothing to run.")
        return

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    device_ports = [p.strip() for p in args.devices.split(",") if p.strip()]
    print(f"[run_rebl] {len(cases)} case(s) across {len(device_ports)} device(s): {device_ports}")

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

    print(f"\n{'=' * 80}\n[run_rebl] BATCH SUMMARY ({len(summary)} case(s))\n{'=' * 80}")
    for r in sorted(summary, key=lambda x: (x["category"], x["case"])):
        print(f"  [dev {r['device']}] {r['category']}/{r['case']}: {r['status']}")
    print("\n[run_rebl] Status tally:")
    for s, n in Counter(r["status"] for r in summary).most_common():
        print(f"  {s}: {n}")
    grand_calls = sum(r.get("tokens", {}).get("calls", 0) for r in summary)
    grand_total = sum(r.get("tokens", {}).get("total_tokens", 0) for r in summary)
    grand_cost = round(sum(r.get("tokens", {}).get("est_cost_usd", 0.0) for r in summary), 4)
    print(f"\n[run_rebl] TOTAL: calls={grand_calls} tokens={grand_total} est_cost=${grand_cost} (Vertex AI billing)")
    try:
        (RESULTS_DIR / "_batch_summary.json").write_text(json.dumps({
            "provider": PROVIDER_NAME,
            "model": model,
            "timeout_seconds": TIMEOUT_SECONDS,
            "auth": "adc (service-account Bearer token, no API key)",
            "cases": summary,
            "totals": {"calls": grand_calls, "total_tokens": grand_total, "est_cost_usd": grand_cost},
            "spend_cap_usd": MAX_SPEND_USD,
            "spend_cap_hit": _SPEND_EXCEEDED.is_set(),
        }, indent=2), encoding="utf-8")
        print(f"[run_rebl] Wrote batch summary -> {RESULTS_DIR / '_batch_summary.json'}")
    except Exception as e:
        print(f"[run_rebl] Warning: could not write batch summary: {e}")


if __name__ == "__main__":
    main()
