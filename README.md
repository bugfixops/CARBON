# CARBON

**Gesture-aware automated reproduction of Android bug reports.**

CARBON is an LLM-driven tool that reads an Android bug report and drives an emulator until the reported failure appears. At each step the LLM sees an annotated screenshot whose numbered boxes match a legend of the screen's elements. It then chooses one of fourteen typed actions. These include parameterized gestures that earlier LLM-driven tools cannot express: pinch-to-zoom, drag-and-drop, region or coordinate swipes, timing-sensitive taps and picker-wheel scrolls. Exceptions from logcat and pixel colours are fed back to the LLM as evidence. Every success the tool reports is checked against six written audit criteria.

The tool is described in the paper *CARBON: Gesture-Aware Automated Reproduction of Android Bug Reports* (under review). This repository contains the tool, the harness that re-ran the baselines, and every run reported in the paper.

## Repository layout

| Path | Contents |
|---|---|
| [`carbon/`](carbon/) | The tool. `reproduction.py` runs the reproduction loop. Screen capture and annotation, the prompt, the action executor and the evidence feedback live beside it. |
| [`baselines/`](baselines/) | AdbGPT and ReActDroid from their authors' code with documented changes, and the harness that ran them and CARBON's repeated runs ([README](baselines/README.md)). |
| [`results/`](results/) | Every run reported in the paper, one folder per campaign: logs, screenshots, audit sheets and per-bug notes. |
| [`prevalence/`](prevalence/) | How often Android bug reports need a gesture: 3,500 randomly sampled reports, their labels and the authors' check ([results](prevalence/RESULTS_sample.md)). |
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
./run.sh results/category-testing-gemini-2.5-pro/double_tap/FossifyOrg_Gallery_847/bug_report.txt
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
| AdbGPT | (no verdict of its own) | 2 of 100 |
| ReActDroid (crash bugs only) | 3 | 3 of 17 |

On ReBL's own 95-bug benchmark, CARBON reproduces 90. Per-bug and per-category results are in [RESULTS.md](RESULTS.md).

| Campaign | Folder | Summary |
|---|---|---|
| 100-bug benchmark: CARBON, its three ablations, ReBL | [`category-testing-gemini-2.5-pro/`](results/category-testing-gemini-2.5-pro/) | [results](results/category-testing-gemini-2.5-pro/RESULTS.md), [audit sheets](results/category-testing-gemini-2.5-pro/audit/) |
| AdbGPT and ReActDroid re-runs | [`baseline-retest-gemini-2.5-pro/`](results/baseline-retest-gemini-2.5-pro/) | [results](results/baseline-retest-gemini-2.5-pro/RESULTS.md) |
| CARBON's repeated runs (16 bugs) | [`carbon-repeated-runs-gemini-2.5-pro/`](results/carbon-repeated-runs-gemini-2.5-pro/) | [results](results/carbon-repeated-runs-gemini-2.5-pro/RESULTS.md) |
| CARBON with GPT-4o | [`CARBON_GPT4o_Dataset/`](results/CARBON_GPT4o_Dataset/) | [results](results/CARBON_GPT4o_Dataset/RESULTS.md) |
| ReBL's benchmark (95 bugs) | [`ReBL_Full_Dataset/`](results/ReBL_Full_Dataset/) | [results](results/ReBL_Full_Dataset/RESULTS.md) |
| ReBL's 9 documented failures | [`ReBL_Failed_Dataset/`](results/ReBL_Failed_Dataset/) | [results](results/ReBL_Failed_Dataset/RESULTS.md) |

## Data

- **APKs.** The 95 APKs of ReBL's benchmark ship in `results/ReBL_Full_Dataset/`. The 100 gesture-benchmark APKs are in the [dataset archive](https://drive.google.com/drive/folders/1j81nyTpwsey1_Z1boODJmEtApxFbLs0v); `baselines/harness/fetch_apk.py <case>` downloads one.
- **Logs.** Run logs are kept as recorded, so paths inside them use the repository's earlier folder names: `Automation/` for `carbon/`, `test_repo/` for `baselines/` and `Dataset/` for `results/`. Local user names, the test devices' account details and the cloud project ID are anonymised; nothing else in the logs was changed.
