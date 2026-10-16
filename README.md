# CARBON

**Gesture-aware automated reproduction of Android bug reports.**

CARBON is an LLM-driven tool that reads an Android bug report and drives an emulator until the reported failure appears. At each step the LLM sees an annotated screenshot whose numbered boxes match a legend of the screen's elements. It then chooses one of fourteen typed actions. These include parameterized gestures that earlier LLM-driven tools cannot express: pinch-to-zoom, drag-and-drop, region or coordinate swipes, timing-sensitive taps and picker-wheel scrolls. Exceptions from logcat and pixel colours are fed back to the LLM as evidence. Every success the tool reports is checked against six written audit criteria.

The tool is described in the paper *CARBON: Gesture-Aware Automated Reproduction of Android Bug Reports* (under review). This repository contains the tool, the harness that re-ran the baselines, and every run reported in the paper.

## Repository layout

| Path | Contents |
|---|---|
| [`carbon/`](carbon/) | The tool. `reproduction.py` runs the reproduction loop. Screen capture and annotation, the prompt, the action executor and the evidence feedback live beside it. |
| [`baselines/`](baselines/) | AdbGPT and ReActDroid from their authors' code with documented changes, and the harness that ran them and CARBON's repeated runs ([README](baselines/README.md)). |
| [`results/`](results/) | Every run reported in the paper, one folder per campaign: logs, screenshots and per-bug notes. |
| [`prevalence/`](prevalence/) | How often Android bug reports need a gesture: 2,597 GUI-reproducible reports from a random sample of 3,500, and their labels ([README](prevalence/README.md)). |
| [`audit/`](audit/) | Every audit in the paper: the two authors' check of the prevalence labels, and the audit of each tool's success claims ([README](audit/README.md)). |
| [`RESULTS.md`](RESULTS.md) | Per-bug results of all four tools on the 100-bug benchmark. |
| `run.sh` | Starts an emulator and reproduces one bug report. |
| `requirements.txt`, `.env.example` | Python dependencies and the LLM configuration template. |

## Requirements

- Python 3.9 or later.
- The Android SDK with an emulator. A Pixel 4, Android 14 (API 34) image with Google APIs matches the experiments.
- A vision-capable LLM: Gemini 2.5 Pro by default.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # then set LLM_API_KEY (a Gemini key by default)
```

If you don't have an emulator, create one in Android Studio (Device Manager, Pixel 4, API 34). `run.sh` uses a running emulator or boots one named `Pixel_4`; set `AVD_NAME` to use another.

## Reproduce a bug report

```bash
adb install -r -t <app.apk>
./run.sh results/carbon-test-gemini-2.5-pro/double_tap/FossifyOrg_Gallery_847/bug_report.txt
```

`run.sh` starts the emulator if needed, runs the reproduction loop and writes the full log to `carbon/Results/`. Without an argument, it uses the sample report above. For where to get the apps' APKs, see [Data](#data).

## LLM configuration

CARBON reads its LLM settings from `.env`:

```bash
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-api-key
LLM_MODEL=gemini-2.5-pro
```

The screenshot encoding needs a vision-capable model. Every comparison between the four tools uses `gemini-2.5-pro`. The 100-bug benchmark was also run with GPT-4o.

## Results

On the 100-bug gesture benchmark, with the same LLM (Gemini 2.5 Pro) and the same audit for every tool:

| Tool | Successes the tool claimed | Passed the audit |
|---|---:|---:|
| **CARBON** | 92 | **88 of 100** |
| ReBL | 50 | 34 of 100 |
| AdbGPT | — | 2 of 100 |
| ReActDroid | 4 | 4 of 100 |

AdbGPT has no success verdict of its own. ReActDroid passed the audit on 3 of the 17 crash bugs and 1 of the 83 non-crash bugs; one of its 4 claimed crashes does not match the report. Its crash-bug runs are from 2026-10-06 (US$2.00 spend cap per run). Its non-crash runs come from a later CI campaign (2026-10-12/13, US$0.95 cap), in which 5 jobs failed; those 5 bugs count as fails.

On ReBL's own 95-bug benchmark, CARBON reproduces 90. Per-bug and per-category results are in [RESULTS.md](RESULTS.md).

| Campaign | Folder | Summary |
|---|---|---|
| 100-bug benchmark: CARBON, its three ablations, ReBL | [`carbon-test-gemini-2.5-pro/`](results/carbon-test-gemini-2.5-pro/) | [results](results/carbon-test-gemini-2.5-pro/RESULTS.md), [audit sheets](audit/reproduction-claims/gesture-benchmark/) |
| AdbGPT and ReActDroid re-runs; also a copy of ReBL's logs | [`baseline-test-gemini-2.5-pro/`](results/baseline-test-gemini-2.5-pro/) | [results](results/baseline-test-gemini-2.5-pro/RESULTS.md), [audit sheets](audit/reproduction-claims/gesture-benchmark/) |
| 100-bug benchmark: CARBON, re-run 1 | [`carbon-retest-1-gemini-2.5-pro/`](results/carbon-retest-1-gemini-2.5-pro/) | [README](results/carbon-retest-1-gemini-2.5-pro/README.md) |
| 100-bug benchmark: CARBON, re-run 2 | [`carbon-retest-2-gemini-2.5-pro/`](results/carbon-retest-2-gemini-2.5-pro/) | [README](results/carbon-retest-2-gemini-2.5-pro/README.md) |
| CARBON with GPT-4o | [`carbon-test-gpt-4o/`](results/carbon-test-gpt-4o/) | [results](results/carbon-test-gpt-4o/RESULTS.md) |
| ReBL's benchmark (95 bugs) | [`carbon-test-rebl-full-gemini-2.5-pro/`](results/carbon-test-rebl-full-gemini-2.5-pro/) | [results](results/carbon-test-rebl-full-gemini-2.5-pro/RESULTS.md), [audit sheet](audit/reproduction-claims/rebl-benchmark/) |
| ReBL's 9 documented failures | [`carbon-test-rebl-failed-gemini-2.5-pro/`](results/carbon-test-rebl-failed-gemini-2.5-pro/) | [results](results/carbon-test-rebl-failed-gemini-2.5-pro/RESULTS.md), [audit sheet](audit/reproduction-claims/rebl-nine-failures/) |

## Data

- **APKs.** The 95 APKs of ReBL's benchmark are in the [Carbon-Rebl-Dataset](https://github.com/Dibae101/Carbon-Rebl-Dataset) repository, under `rebl/` (stored with Git LFS). The 100 gesture-benchmark APKs are in the [dataset archive](https://drive.google.com/drive/folders/1j81nyTpwsey1_Z1boODJmEtApxFbLs0v); `baselines/harness/fetch_apk.py <case>` downloads one.
- **Logs.** Run logs are kept as recorded, so paths inside them use the repository's earlier folder names: `Automation/` for `carbon/`, `test_repo/` for `baselines/` and `Dataset/` for `results/`. Local user names, the test devices' account details and the cloud project ID are anonymised; nothing else in the logs was changed.
