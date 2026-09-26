"""
Gemini (Vertex AI via ADC) retest batch runner for the carbon-100 timeout cases.

Re-runs the 53 cases that hit the 15-minute cap in the original gpt-4o run
(Dataset/carbon-100/Results/), this time with a 30-minute cap per case and
Gemini 2.5 Flash via Vertex AI as the LLM provider -- authenticated with
Application Default Credentials (service-account Bearer token). No API key
exists in this flow: the account's org policy disallows creating API keys,
so my_gpt.py mints a short-lived OAuth2 token from the service-account JSON
at GOOGLE_APPLICATION_CREDENTIALS (written from the GCP_SA_JSON secret).

Reuses the shared machinery from run_retest_groq (case list, APK acquisition,
install/launch, checkpointing, threading driver); only the provider-specific
pieces (results dir, child env, validation) live here.

Honest-logging rules (do not "fix" these):
  * The per-case log header is printed by my_gpt.py from the live config, so it
    always shows the TRUE provider/model, e.g.
    [LLM] Provider: vertex-adc | Model: gemini-2.5-pro | Vision: True
  * The real timeout (default 1800s / 30 min, overridable via GEMINI_TIMEOUT_SECONDS) is written into every case log.
  * Results go to Dataset/carbon-100/Results-gemini-retest/ -- never into the
    original Dataset/carbon-100/Results/ folder.
  * Vertex AI bills GCP credits: per-case token sidecars carry the real
    est_cost_usd computed from the API's usageMetadata.

Usage (single device, e.g. inside android-emulator-runner):
    python run_retest_gemini.py 5554 --model gemini-2.5-pro

Smoke test (1 case):
    python run_retest_gemini.py 5554 --case long_press/FossifyOrg_Messages_641

Wave sharding across a 10-job matrix (job N of 10):
    python run_retest_gemini.py 5554 --shard 3 --of 10

Environment:
    GOOGLE_APPLICATION_CREDENTIALS   path to the service-account JSON
                                     (the workflow writes it from GCP_SA_JSON)
    GCP_PROJECT_ID                   optional override (else read from the JSON)
    VERTEX_LOCATION                  optional override (default us-central1)
    GEMINI_MODEL                     overrides --model
    GEMINI_MAX_SPEND_USD             per-job spend cap (default 8.00); the job aborts
                                     remaining cases once cumulative est_cost_usd hits it
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

import run_retest_groq as base  # shared: TIMEOUT_CASES, APK/install/checkpoint machinery

AUTOMATION_DIR = base.AUTOMATION_DIR
REPO_ROOT = base.REPO_ROOT
# Override per run via GEMINI_TIMEOUT_SECONDS (e.g. 2700 for 45 min);
TIMEOUT_SECONDS = int(os.environ.get("GEMINI_TIMEOUT_SECONDS", base.TIMEOUT_SECONDS))
FINAL_MARKER = base.FINAL_MARKER
WORK_ROOT = base.WORK_ROOT
APK_DIR = base.APK_DIR

# NEW results folder -- never mix with Dataset/carbon-100/Results/ or Results-groq-retest/.
RESULTS_DIR = REPO_ROOT / "Dataset" / "carbon-100" / "Results-gemini-retest"

PROVIDER_NAME = "vertex-adc"
DEFAULT_MODEL = "gemini-2.5-pro"

# Hard spend guardrail: abort remaining cases once the cumulative estimated
# Vertex AI cost for THIS job reaches the cap. Each wave shard enforces its own
# cap, so the worst-case wave total is MAX_SPEND_USD * shard-count
# (default $8 x 10 = $80) -- under the $300 trial credit; sized for
# gemini-2.5-pro at ~$1.08/case x ~6 cases/shard.
# Override per run via GEMINI_MAX_SPEND_USD.
MAX_SPEND_USD = float(os.environ.get("GEMINI_MAX_SPEND_USD", "8.00"))
_SPEND_LOCK = threading.Lock()
_SPEND_USD = 0.0
_SPEND_EXCEEDED = threading.Event()

# Point the shared checkpoint helper at OUR results dir: resolve_cases ->
# _already_concluded reads this module global from run_retest_groq.
base.RESULTS_DIR = RESULTS_DIR


def _adc_ok():
    p = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    return bool(p and Path(p).is_file())


def run_one_case(device_port, category, case_folder, bug_report, model):
    """One case with the Gemini/Vertex-ADC child env (otherwise shared logic)."""
    log_prefix = f"[dev {device_port}]"
    case_results_dir = RESULTS_DIR / category / case_folder
    case_results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    log_path = case_results_dir / f"{timestamp}.log"

    banner = (f"[run_retest] CASE {category}/{case_folder} | provider={PROVIDER_NAME} | "
              f"model={model} | timeout={TIMEOUT_SECONDS}s ({TIMEOUT_SECONDS // 60} min) | device={device_port}")
    print(f"\n{'=' * 80}\n{banner}\n{'=' * 80}")

    def finalize(status, extra=""):
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"\n{FINAL_MARKER}{status}{extra}\n")
        return {"device": device_port, "category": category, "case": case_folder,
                "status": status, "log": str(log_path)}

    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        lf.write(banner + "\n")

    # 1. APK (shared)
    try:
        apk_path = base.ensure_apk(category, case_folder, bug_report, log_prefix)
    except base.APKUnavailableError as e:
        print(f"{log_prefix} {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"[run_retest] {e}\n")
        return finalize("apk_unavailable")

    # 2. device install/launch (shared)
    device = base.u2.connect(f"emulator-{device_port}")
    package_name, was_launcher = None, False
    try:
        package_name, was_launcher = base.install_and_launch(device, apk_path, log_prefix)
    except Exception as e:
        print(f"{log_prefix} FAILED to install/launch {apk_path.name}: {e}")
        with open(log_path, "a", encoding="utf-8", errors="replace") as lf:
            lf.write(f"[run_retest] INSTALL_FAILED: {e}\n")
        return finalize("install_failed")

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
            log_file.write(f"\n[run_retest] FAILED: exceeded {TIMEOUT_SECONDS}s "
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
                lf.write(f"\n[run_retest] token usage: calls={tokens['calls']} "
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
            category, case_folder, bug_report = case_queue.pop(0)
        result = run_one_case(device_port, category, case_folder, bug_report, model)
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
        description="Gemini (Vertex AI via ADC) retest of the carbon-100 timeout cases (30-min cap)")
    parser.add_argument("devices", help="Comma-separated emulator ports, e.g. 5554")
    parser.add_argument("--model", default=None,
                        help="Vertex AI model id (default: GEMINI_MODEL env or gemini-2.5-pro)")
    parser.add_argument("--category", default=None)
    parser.add_argument("--case", default=None, help="Single case: 'category/folder' (suffix ' Tested' optional)")
    parser.add_argument("--cases", default=None, help="Comma-separated 'category/folder' list")
    parser.add_argument("--shard", type=int, default=None, help="This job's shard index (0-based)")
    parser.add_argument("--of", type=int, default=None, help="Total shard count")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    model = args.model or os.environ.get("GEMINI_MODEL", "") or DEFAULT_MODEL
    if not _adc_ok():
        sys.exit("[run_retest] FATAL: GOOGLE_APPLICATION_CREDENTIALS is not set to an "
                 "existing service-account JSON file. (The workflow writes it from the "
                 "GCP_SA_JSON secret; see run_shard_gemini.sh.)")
    # Fail fast (no billable call): minting a token catches a bad SA file now,
    # not 5 minutes into the first case.
    try:
        import google.auth
        from google.auth.transport.requests import Request as _GARequest
        creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        creds.refresh(_GARequest())
    except Exception as e:
        sys.exit(f"[run_retest] FATAL: could not mint ADC access token: {e}")
    print(f"[run_retest] provider={PROVIDER_NAME} model={model} timeout={TIMEOUT_SECONDS}s "
          f"({TIMEOUT_SECONDS // 60} min) ADC token minted OK")
    print(f"[run_retest] spend cap: ${MAX_SPEND_USD:.2f} per job "
          f"(GEMINI_MAX_SPEND_USD); wave ceiling = cap x shard count")

    # Gemini retest pool = the 53 timeout cases PLUS the 8 non-timeout failures
    # (loop trips / harness error) from the original run -- "every one which
    # failed". The Groq entrypoint keeps the default pool (TIMEOUT_CASES only).
    cases = base.resolve_cases(case=args.case, cases=args.cases, category=args.category,
                               limit=args.limit, shard=args.shard, of=args.of,
                               pool=base.TIMEOUT_CASES + base.EXTRA_FAILED_CASES)
    if not cases:
        print("[run_retest] No matching cases. Nothing to run.")
        return

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    APK_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    device_ports = [p.strip() for p in args.devices.split(",") if p.strip()]
    print(f"[run_retest] {len(cases)} case(s) across {len(device_ports)} device(s): {device_ports}")

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

    print(f"\n{'=' * 80}\n[run_retest] BATCH SUMMARY ({len(summary)} case(s))\n{'=' * 80}")
    for r in sorted(summary, key=lambda x: (x["category"], x["case"])):
        print(f"  [dev {r['device']}] {r['category']}/{r['case']}: {r['status']}")
    print("\n[run_retest] Status tally:")
    for s, n in Counter(r["status"] for r in summary).most_common():
        print(f"  {s}: {n}")
    grand_calls = sum(r.get("tokens", {}).get("calls", 0) for r in summary)
    grand_total = sum(r.get("tokens", {}).get("total_tokens", 0) for r in summary)
    grand_cost = round(sum(r.get("tokens", {}).get("est_cost_usd", 0.0) for r in summary), 4)
    print(f"\n[run_retest] TOTAL: calls={grand_calls} tokens={grand_total} est_cost=${grand_cost} (Vertex AI billing)")
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
        print(f"[run_retest] Wrote batch summary -> {RESULTS_DIR / '_batch_summary.json'}")
    except Exception as e:
        print(f"[run_retest] Warning: could not write batch summary: {e}")


if __name__ == "__main__":
    main()
