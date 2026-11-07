# CARBON

**Gesture-aware automated reproduction of Android bug reports.**

CARBON is an LLM-driven tool that reads an Android bug report and operates an emulator until the reported bug appears. At each step, the LLM sees an annotated screenshot whose numbered boxes match a list of the screen's elements, and it chooses one of fourteen actions. These include gestures that earlier LLM-based tools cannot perform: pinch-to-zoom, drag-and-drop, precise swipes, timing-sensitive taps, and picker-wheel turns. After each action, CARBON reports new logcat exceptions and screen color changes to the LLM as evidence. Every success claim is checked by a manual audit.

The tool is described in the paper *CARBON: Gesture-Aware Automated Reproduction of Android Bug Reports* (under review). This repository contains the tool, every run reported in the paper, and the audits.

## Repository layout

| Path | Contents |
|---|---|
| [`carbon/`](carbon/) | The tool. `reproduction.py` runs the reproduction loop; screen capture and annotation, the prompt, the action executor, and the evidence feedback are beside it. |
| [`results/`](results/) | Every run reported in the paper, one folder per campaign: logs, screenshots, per-bug notes, and each bug's `bug_report.txt`. |
| [`audit/`](audit/) | The prevalence study ([`audit/prevalence/`](audit/prevalence/)), the one-author audit of its labels ([`audit/prevalence-labels/single-author/`](audit/prevalence-labels/single-author/)), and the audit of every tool's success claims ([`audit/reproduction-claims/`](audit/reproduction-claims/)). See the [README](audit/README.md). |
| [`RESULTS.md`](RESULTS.md) | Per-bug results of all four tools on the 100-bug gesture benchmark. |
| `run.sh` | Starts an emulator and reproduces one bug report. |
| `requirements.txt`, `.env.example` | Python dependencies and the LLM configuration template. |

## Datasets

- **APKs.** The APKs of both benchmarks are in [bugfixops/Carbon-Rebl-Dataset](https://github.com/bugfixops/Carbon-Rebl-Dataset), stored with Git LFS: `carbon-100/` holds the 100-bug gesture benchmark (one folder per category and bug), and `rebl/` holds ReBL's benchmark (`crash/` and `non_crash/`).
- **Bug reports.** Each bug's report is in its run folder as `bug_report.txt`: [`results/carbon-test-gemini-2.5-pro/`](results/carbon-test-gemini-2.5-pro/) for the gesture benchmark and [`results/carbon-test-rebl-full-gemini-2.5-pro/`](results/carbon-test-rebl-full-gemini-2.5-pro/) for ReBL's benchmark.
- **Prevalence study.** The 3,500 sampled reports, their labels, and the counting scripts are in [`audit/prevalence/`](audit/prevalence/).

## Baselines

ReBL, AdbGPT, and ReActDroid are not part of this repository. They ran from their authors' code, with the small changes listed in Section 4.3 of the paper:

| Tool | Repository | Commit |
|---|---|---|
| ReBL | [datareviewtest/ReBL](https://github.com/datareviewtest/ReBL) | `8c9ce57` |
| AdbGPT | [sidongfeng/AdbGPT](https://github.com/sidongfeng/AdbGPT) | `ec29b4b` |
| ReActDroid | [wuchiuwong/ReActDroid](https://github.com/wuchiuwong/ReActDroid) | `6bde9cd` |

Their run logs are in [`results/`](results/).

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

`run.sh` starts the emulator if needed, runs the reproduction loop, and writes the full log to `carbon/Results/`. Without an argument, it uses the sample report above. The apps' APKs are in the [dataset repository](#datasets).

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

AdbGPT has no success verdict of its own. ReActDroid detects only crashes: it passed the audit on 3 of the 17 crash bugs and 1 of the 83 non-crash bugs, and one of its 4 claimed crashes does not match the report.

On ReBL's own benchmark, CARBON reproduces 90 of 95 bugs. Per-bug and per-category results are in [RESULTS.md](RESULTS.md).

| Campaign | Folder | Summary |
|---|---|---|
| 100-bug benchmark: CARBON, its three ablations, ReBL | [`carbon-test-gemini-2.5-pro/`](results/carbon-test-gemini-2.5-pro/) | [results](results/carbon-test-gemini-2.5-pro/RESULTS.md), [audit sheets](audit/reproduction-claims/gesture-benchmark/) |
| AdbGPT and ReActDroid; also a copy of ReBL's logs | [`baseline-test-gemini-2.5-pro/`](results/baseline-test-gemini-2.5-pro/) | [results](results/baseline-test-gemini-2.5-pro/RESULTS.md), [audit sheets](audit/reproduction-claims/gesture-benchmark/) |
| 100-bug benchmark: CARBON, re-run 1 | [`carbon-retest-1-gemini-2.5-pro/`](results/carbon-retest-1-gemini-2.5-pro/) | [README](results/carbon-retest-1-gemini-2.5-pro/README.md) |
| 100-bug benchmark: CARBON, re-run 2 | [`carbon-retest-2-gemini-2.5-pro/`](results/carbon-retest-2-gemini-2.5-pro/) | [README](results/carbon-retest-2-gemini-2.5-pro/README.md) |
| CARBON with GPT-4o | [`carbon-test-gpt-4o/`](results/carbon-test-gpt-4o/) | [results](results/carbon-test-gpt-4o/RESULTS.md) |
| ReBL's benchmark (95 bugs) | [`carbon-test-rebl-full-gemini-2.5-pro/`](results/carbon-test-rebl-full-gemini-2.5-pro/) | [results](results/carbon-test-rebl-full-gemini-2.5-pro/RESULTS.md), [audit sheet](audit/reproduction-claims/rebl-benchmark/) |
| ReBL's 9 documented failures | [`carbon-test-rebl-failed-gemini-2.5-pro/`](results/carbon-test-rebl-failed-gemini-2.5-pro/) | [results](results/carbon-test-rebl-failed-gemini-2.5-pro/RESULTS.md), [audit sheet](audit/reproduction-claims/rebl-nine-failures/) |

Run logs are kept as recorded, so paths inside them use the repository's earlier folder names, such as `Automation/` for `carbon/` and `Dataset/` for `results/`. Local user names, the test devices' account details, and the cloud project ID are anonymised; nothing else in the logs was changed.
