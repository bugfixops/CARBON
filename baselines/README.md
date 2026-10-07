# Baselines and run harness

This folder re-runs the two baselines, AdbGPT and ReActDroid, from their authors' published code. It changes only what is needed to run them with Gemini 2.5 Pro on the same emulator setup as CARBON. [UPSTREAM.md](UPSTREAM.md) lists every change and its reason. The same harness also ran CARBON's repeated runs and the running-example run. The runs reported in the paper are in [`../results/baseline-retest-gemini-2.5-pro/`](../results/baseline-retest-gemini-2.5-pro/RESULTS.md) and [`../results/carbon-repeated-runs-gemini-2.5-pro/`](../results/carbon-repeated-runs-gemini-2.5-pro/RESULTS.md).

```
baselines/
  AdbGPT/                 sidongfeng/AdbGPT @ ec29b4b + [CARBON-RETEST] edits
  ReActDroid/             wuchiuwong/ReActDroid @ 6bde9cd + [CARBON-RETEST] edits
  harness/
    run_baselines.py      runs a tool over the benchmark, one case at a time
    preflight.py          checks the setup before any LLM spend
    cost.py               cost projection, and real spend from the logs
    gemini_client.py      the shared Gemini client; logs every call's tokens
    device.py             device preparation (same as CARBON), logcat, recording
    cases_manifest.json   100 cases: APK + Drive id, package, activity, report version, crash/non-crash
    extra_cases.json      cases outside the benchmark, run only when named with --cases (Memento#169)
    variance_cases.json   the 16 cases of CARBON's repeated runs
    apk_sources.json      where each case's APK is in the dataset archive on Google Drive
    fetch_apk.py          downloads one case's APK from the archive (or uses one committed beside the report)
    index_drive.py        rebuilds apk_sources.json from the Drive folder
    build_manifest.py     regenerates cases_manifest.json
    summarize.py          per-tool runs.csv, audit.csv and a summary
  setup.sh                creates .venv-adbgpt and .venv-reactdroid (Python 3.10)
  requirements-*.txt      each tool's Python dependencies
  check_upstream.sh       prints the full diff against the upstream commits
  results/                one folder per run (created when you run; not tracked)
```

## 1. Setup

1. **System tools.** You need the Android SDK with an Android 14 emulator, Java, Python 3.10, and Node with Appium. `./setup.sh` lists anything missing, with the install command, and then creates both virtualenvs. For CARBON runs, create `.venv-carbon` the same way from `requirements-carbon.txt`, or pass `--python`.
2. **LLM credentials.** These come from the repository's `.env`, the same file CARBON uses:
   ```
   LLM_PROVIDER=vertex
   LLM_API_KEY=...
   ```
   To use a service account instead, set `LLM_PROVIDER=vertex-adc` and `GCP_PROJECT_ID`.
3. **APKs.** The 100 benchmark APKs are not in git; they are in the dataset archive on Google Drive. To download one case's APK:
   ```
   python harness/fetch_apk.py <case> --out apks
   ```
   This needs `pip install gdown`. Then pass `--apk-root apks`, or put each APK in its case folder.
4. **Emulator.** Start a Pixel 4 / API 34 emulator and load the seed media, as for CARBON (from the repository root):
   ```
   ./run.sh                                  # or start the AVD yourself
   python3 carbon/push_seed_media.py 5554
   ```
5. **Appium (ReActDroid only).** Keep it running in another terminal:
   ```
   appium --base-path /wd/hub
   ```

## 2. Check before spending

Run these from `baselines/`:

```
.venv-adbgpt/bin/python     harness/preflight.py --tool adbgpt     --llm
.venv-reactdroid/bin/python harness/preflight.py --tool reactdroid --llm
```

`--llm` makes one Gemini call, about US$0.001. Every check must pass. `run_baselines.py --dry-run` lists the selected cases and whether each APK is found, without using a device or the LLM.

## 3. Run

```
.venv-adbgpt/bin/python     harness/run_baselines.py --tool adbgpt     --resume   # all 100 bugs
.venv-reactdroid/bin/python harness/run_baselines.py --tool reactdroid --resume   # the 17 crash bugs
```

**Options:**
- `--cases a,b` runs only the named cases. A two-case pilot, such as `FossifyOrg_Calendar_1035,FossifyOrg_Gallery_363`, followed by `harness/cost.py actual`, projects the full cost.
- `--resume` skips cases that already have a completed run. A case whose setup failed before the tool started (install error, emulator offline) is run again. A run that started is never repeated: it counts as is.
- `--budget 1800` is the time per run, as in the paper.
- `--spend-cap 3` is the USD per run (`0` disables it). It stops runaway AdbGPT replays, which re-send the whole conversation on every call. A capped run is recorded as `spend_cap` and counts as a failure. The paper's AdbGPT runs used US$2.50.
- `--scope all` runs ReActDroid on all 100 bugs. ReActDroid only stops on a crash, so on the 83 non-crash bugs it can only use the full 30 minutes and fail. Its own paper evaluates crashes only.
- `--reactdroid-input full` gives ReActDroid the whole bug report instead of the one-sentence title its paper uses.
- `--serial emulator-5556` selects another emulator. Two emulators can run in parallel, one process each. For ReActDroid, use one Appium server per emulator (`--appium-url`).

**Each run writes `results/<tool>/<case>/<timestamp>/`:**

| File | Contents |
|---|---|
| `run.json` | Status (`finished`, `timeout`, `spend_cap`, `error`, `setup_failed`), the tool's own claim, app crashes from logcat, LLM calls/tokens/cost, versions |
| `tool_stdout.log` | The tool's full output |
| `logcat.txt` | Main/system/crash buffers with PIDs |
| `recording/` | Screen recording, in 170 s segments (`--no-record` skips it) |
| `final.png` | Last screen |
| `llm_usage.jsonl` | One line per Gemini call, with thinking tokens |
| `adbgpt_output/` | AdbGPT only: its per-step screenshots and hierarchies, and `loguru.log` |
| `ReActDroid/Data/` | ReActDroid only: its chat logs and page memory |

`results/<tool>/runs.csv` has one row per run; `harness/summarize.py` writes the audit sheet.

## 4. Deciding success (manual audit)

Every run is recorded as `PENDING_AUDIT`. The harness does not decide success because neither tool can:
- AdbGPT only replays steps and has no check of its own; its paper judged reproduction by hand.
- ReActDroid's check accepts a crash in any process.

Each run is audited with the paper's six criteria:

- **Crash bug:** success only if `run.json` → `logcat.app_events` shows a crash or ANR **in the app's own process** that matches the report. A crash of another process does not count.
- **Non-crash bug:** success only if the recording or screenshots show the reported symptom after the reported trigger.
- `timeout`, `spend_cap` and `error` runs are failures unless the symptom clearly appeared before the stop.

## 5. CARBON's repeated runs

The repeated runs re-run CARBON itself (`carbon/reproduction.py`, unchanged) through this harness on a fixed sample.

- **Sample:** [harness/variance_cases.json](harness/variance_cases.json) lists 16 cases, 2 per gesture category, drawn with a fixed seed before any re-run and without looking at the original outcomes.
- **Setup:** as in the paper's Gemini run: `gemini-2.5-pro` at temperature 0.3, CARBON's device preparation with no pre-granted permissions, and the 1,800 s budget.
- **Loop guard switched off:** `reproduction.py` has a loop guard (`REBL_MAX_REPEAT`) that was added after the main run and never fired in its logs. The harness switches it off, and `run.json` records this under `carbon_env`.
- **Cost** is read from CARBON's token sidecar (`carbon_tokens.json`), including thinking tokens.

Each case ran twice, which is two invocations of:

```
CASES=$(python3 -c "import json; print(','.join(c['case'] for c in json.load(open('harness/variance_cases.json'))['cases']))")
.venv-carbon/bin/python harness/run_baselines.py --tool carbon --cases "$CASES" --no-record --spend-cap 3
```

## 6. Running-example run (Memento#169)

Memento-Calendar#169, the paper's running example, comes from ReBL's benchmark, not the 100-bug set. [harness/extra_cases.json](harness/extra_cases.json) defines it, with the APK committed beside its bug report in `results/ReBL_Full_Dataset/`. Android 14 refuses to install an app that targets SDK < 23, so for such an APK the harness repeats `adb install` with `--bypass-low-target-sdk-block`; the APK is unchanged.

```
.venv-carbon/bin/python harness/run_baselines.py --tool carbon --cases alexstyl_Memento-Calendar_169 --spend-cap 3
```

## Environment of the reported runs

The baseline runs, CARBON's repeated runs and the Memento run each used a fresh x86_64 Pixel 4 / Android 14 emulator on a GitHub-hosted Linux runner, one job per run. CARBON's main benchmark runs used an ARM emulator of the same device and Android version on an Apple-silicon workstation. The x86_64 image uses software rendering and is slower, which can affect timing-sensitive bugs.
