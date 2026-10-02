# CARBON

**CARBON: Gesture-Aware Automated Reproduction
of Android Bug Reports**

CARBON is an LLM-driven system for automatically reproducing Android bug
reports. It connects to an Android emulator, captures annotated screenshots
with color-coded bounding boxes, and uses Gemini 2.5 Pro to iteratively follow
bug reproduction steps — including complex gestures like pinch-to-zoom,
drag-and-drop, region/coordinate swipes, and timing-sensitive taps that previous
tools could not handle. A dual oracle (logcat + view-hierarchy state) verifies that
the bug symptom is actually triggered rather than trusting the LLM's
self-report.

---

## Repository layout

```
Automation/      CARBON tool: capture, multi-modal encoding, action executor, dual oracle
Dataset/         One folder per testing campaign (see "Dataset" below):
  category-testing-gemini-2.5-pro/  100-bug gesture-diverse benchmark, 8 gesture categories
  ReBL_Failed_Dataset/       9-bug ReBL documented-failure set (the paper's cited artifact)
  ReBL_Full_Dataset/         95-bug ReBL-dataset campaign, CARBON on Gemini 2.5 Pro
  CARBON_GPT4o_Dataset/      the same 100-bug benchmark run with GPT-4o (logs only)
Results-retest-merge/  188 raw timestamped CARBON run logs for the 100-bug benchmark,
                 mirroring Dataset/'s 8 gesture categories and the same bug folder
                 names; CARBON_GPT4o_Dataset/RESULTS.md is built from these logs
gesture_prevalence/  crawl and keyword classification of 3,629 randomly sampled
                 Android bug reports, measuring how often a report needs a gesture
                 beyond tap/text (see its own README.md)
run.sh           One-command runner (boots emulator, runs a bug report)
requirements.txt Python dependencies
.env.example     LLM configuration template
RESULTS.md       Full per-bug comparison results
```

---

## Requirements

- **Python 3.9+**
- **Android SDK** with an emulator (AVD). A **Pixel 4, Android 14 (API 34)**
  image with Google APIs matches the configuration used in our experiments.
- A vision-capable **LLM API key** (Gemini by default; see options below).

---

## Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure your LLM key
cp .env.example .env
#    then edit .env and set LLM_API_KEY=...   (a Gemini key by default)
```

Create an emulator if you don't have one (Android Studio → Device Manager →
Pixel 4, API 34). The runner auto-detects a running emulator, or boots one
named `Pixel_4` (override with `AVD_NAME`).

---

## Running

```bash
# Install the bug's APK once, then reproduce it
adb install -r -t "Dataset/category-testing-gemini-2.5-pro/double_tap/FossifyOrg_Gallery_847 Tested/gallery-24-foss-release.apk"
./run.sh "Dataset/category-testing-gemini-2.5-pro/double_tap/FossifyOrg_Gallery_847 Tested/bug_report.txt"

# With no argument, a sample bug is used
./run.sh
```

`run.sh` boots the emulator (if needed), runs the reproduction loop, and
streams a full log to `Automation/Results/`.

---

## LLM configuration

CARBON uses **Google Gemini 2.5 Pro** (a vision-capable model), configured in
`.env`:

```bash
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-api-key-here
LLM_MODEL=gemini-2.5-pro
```

The screenshot encoding requires a vision-capable model. The four-tool comparison
below is measured on `gemini-2.5-pro`, as is the ReBL-dataset campaign. The
100-bug gesture benchmark was additionally run end-to-end on **GPT-4o** as a
second backing model, reported separately in
[Dataset/CARBON_GPT4o_Dataset/RESULTS.md](Dataset/CARBON_GPT4o_Dataset/RESULTS.md).

---

## Dataset

`Dataset/` holds one folder per testing campaign.

**`category-testing-gemini-2.5-pro/`** — the 100-bug gesture-diverse benchmark across eight
gesture categories. Each bug folder includes the verbatim `bug_report.txt`, per-tool
execution logs (CARBON, ReBL, AdbGPT, ReActDroid), the three ablation logs under
`abalation-tests/`, and an `Annotation/` example. This is the set the headline results
below are measured on. Counts and the reason for each of CARBON's 12 failures:
[Dataset/category-testing-gemini-2.5-pro/RESULTS.md](Dataset/category-testing-gemini-2.5-pro/RESULTS.md).

**`ReBL_Failed_Dataset/`** — the 9-bug ReBL documented-failure set, kept unchanged as the
artifact the paper cites.

**`ReBL_Full_Dataset/`** — the full ReBL-dataset campaign: 95 bug reports run by CARBON on
Gemini 2.5 Pro, 90 of 95 reproduced. A different dataset and a separate campaign from the
100-bug benchmark, so its numbers are not comparable to the tables below. Each case folder
unifies the case's inputs (report, APK, metadata) with its run log. The 9 bugs in
`ReBL_Failed_Dataset/` are a curated subset of these 95, kept separately on purpose. Counts
and the reason for each of the 5 non-reproductions:
[Dataset/ReBL_Full_Dataset/RESULTS.md](Dataset/ReBL_Full_Dataset/RESULTS.md).

**`CARBON_GPT4o_Dataset/`** — CARBON's GPT-4o run over the same 100-bug benchmark, grouped
as a set: **81 of 100**. Each log also lives beside its bug in `category-testing-gemini-2.5-pro/`.
Counts and the reason for each of the 19 failures: [Dataset/CARBON_GPT4o_Dataset/RESULTS.md](Dataset/CARBON_GPT4o_Dataset/RESULTS.md);
folder layout: [Dataset/CARBON_GPT4o_Dataset/README.md](Dataset/CARBON_GPT4o_Dataset/README.md);
cross-model comparison: [CARBON_gemini-2.5-pro_vs_gpt-4o.md](Dataset/CARBON_gemini-2.5-pro_vs_gpt-4o.md).

> **APKs — the two campaigns differ.** The 95 ReBL-dataset case APKs ship **in this
> repository**, under `Dataset/ReBL_Full_Dataset/`. The 100 gesture-benchmark APKs do
> **not** ship in-repo: they are large and are distributed only through the dataset archive
> below, which is therefore the sole source for them (including the
> `gallery-24-foss-release.apk` used in the "Running" example above).
>
> **Dataset archive (APKs + logs):** _https://drive.google.com/drive/folders/1j81nyTpwsey1_Z1boODJmEtApxFbLs0v?usp=drive_link_

---

## Results

Evaluated on **100 Android bug reports** against ReBL, ReActDroid, and AdbGPT,
all run on the same emulator and the same Gemini 2.5 Pro model.

### Overall

Every tool declares success by self-report, so we re-audit each nominal success
against a uniform six-criterion legitimacy check (a verdict in the tool's own
log, at least one real action, more than 10 s runtime, a complete log, a
corroborating crash/state signal, and no contradicting hedge). Counts are
**nominal** (self-reported) vs. **audit-clean** (verified).

| Tool | Nominal success | Audit-clean success | Audit-clean rate |
|------|-----------------|---------------------|------------------|
| **CARBON** | **92** | **88** | **88.0%** |
| ReBL | 50 | 34 | 34.0% |
| ReActDroid | 5 | 5 | 5.0% |
| AdbGPT | 54 | 4 | 4.0% |

CARBON’s dual oracle confirmed 88 of 92 LLM declarations. ReBL's 50 self-reported
successes drop to 34 (16 non-crash claims with no supporting signal). AdbGPT's
54 drop to 4: the other 50 count a fallback `[MISSING]` tap as completion
without ever reaching the symptom. ReActDroid's 5 (all crashes) stand.

> **Second backing model.** CARBON was also run over these same 100 bugs with
> **GPT-4o**, reaching 81/100 under that campaign's own resolution rule — see
> [Dataset/CARBON_GPT4o_Dataset/RESULTS.md](Dataset/CARBON_GPT4o_Dataset/RESULTS.md).
> That figure is not produced by the six-criterion audit above, so it is not a
> like-for-like model delta against 88. The four-tool comparison on this page is
> Gemini 2.5 Pro throughout.

### Per-category

| Category | Bugs | CARBON | ReBL | ReActDroid | AdbGPT |
|----------|------|--------|------|------------|--------|
| Double Tap | 21 | 18/21 | 9/21 | 2/21 | 0/21 |
| Drag & Drop | 9 | 8/9 | 1/9 | 0/9 | 0/9 |
| Long Press | 9 | 8/9 | 2/9 | 0/9 | 0/9 |
| Orientation | 6 | 5/6 | 4/6 | 0/6 | 0/6 |
| Pinch/Zoom | 12 | 12/12 | 1/12 | 0/12 | 1/12 |
| Quick Tap | 7 | 5/7 | 0/7 | 0/7 | 0/7 |
| Scroll | 6 | 6/6 | 3/6 | 2/6 | 2/6 |
| Swipe | 30 | 26/30 | 14/30 | 1/30 | 1/30 |
| *ReBL Failure Challenge Set* | *9* | *7/9* | *0/9* | *—* | *—* |

> Per-category counts are **audit-confirmed**, matching the paper's Table III.
> AdbGPT's pre-audit self-reported total was 54; only 4 survive the audit (the
> other 50 count a fallback `[MISSING]` tap as completion). See RESULTS.md.

### Sample per-bug results

A few representative bugs (✅ reproduced · ❌ not reproduced):

| Bug ID | App | CARBON | ReBL | ReActDroid | AdbGPT | Summary |
|--------|-----|--------|------|------------|--------|---------|
| [FossifyOrg_Gallery_847](Dataset/category-testing-gemini-2.5-pro/double_tap/FossifyOrg_Gallery_847%20Tested) | FossifyOrg/Gallery | ✅ | ❌ | ❌ | ✅ | Invalid "fill screen" zoom for GIF images on double-tap |
| [FossifyOrg_Paint_25](Dataset/category-testing-gemini-2.5-pro/pinch_zoom/FossifyOrg_Paint_25%20Tested) | FossifyOrg/Paint | ✅ | ❌ | ❌ | ✅ | Eraser size not relative to zoom at minimum brush size (pinch) |
| [MetrolistGroup_Metrolist_3227](Dataset/category-testing-gemini-2.5-pro/drag_and_drop/MetrolistGroup_Metrolist_3227%20Tested) | MetrolistGroup/Metrolist | ✅ | ❌ | ❌ | ❌ | Drag-to-reorder corrupts playlist order |
| [alexstyl_Memento-Calendar_169](Dataset/ReBL_Failed_Dataset/crash/alexstyl_Memento-Calendar_169) | alexstyl/Memento-Calendar | ✅ | ❌ | — | — | Custom-view date picker crash (ReBL failure set) |

**-> See the full per-bug breakdown for all 100 + 9 bugs in [RESULTS.md](RESULTS.md)**, including
per-tool verdicts, annotated screenshots, reproduction steps, and the legitimacy
audit notes for each tool.
