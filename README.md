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
BugCrawler/      GitHub crawler used to build the gesture-diverse benchmark
Dataset/         100-bug benchmark + ReBL failure set (see "Dataset" below)
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
adb install -r -t "Dataset/double_tap/FossifyOrg_Gallery_847 Tested/gallery-24-foss-release.apk"
./run.sh "Dataset/double_tap/FossifyOrg_Gallery_847 Tested/bug_report.txt"

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

The screenshot encoding requires a vision-capable model; all reported results
use `gemini-2.5-pro`.

---

## Dataset

`Dataset/` contains the 100-bug gesture-diverse benchmark across eight gesture
categories, plus the 9-bug ReBL documented-failure set. Each bug folder
includes the verbatim `bug_report.txt`, the runnable APK at the cited version,
per-tool execution logs (CARBON, ReBL, AdbGPT, ReActDroid), the three ablation
logs under `abalation-tests/`, and an `Annotation/` example.

> **APKs:** the benchmark ships with one runnable APK per bug. Because the full
> set of APKs is large, it is also mirrored in the dataset archive linked here:
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
| [FossifyOrg_Gallery_847](Dataset/double_tap/FossifyOrg_Gallery_847%20Tested) | FossifyOrg/Gallery | ✅ | ❌ | ❌ | ✅ | Invalid "fill screen" zoom for GIF images on double-tap |
| [FossifyOrg_Paint_25](Dataset/pinch_zoom/FossifyOrg_Paint_25%20Tested) | FossifyOrg/Paint | ✅ | ❌ | ❌ | ✅ | Eraser size not relative to zoom at minimum brush size (pinch) |
| [MetrolistGroup_Metrolist_3227](Dataset/drag_and_drop/MetrolistGroup_Metrolist_3227%20Tested) | MetrolistGroup/Metrolist | ✅ | ❌ | ❌ | ❌ | Drag-to-reorder corrupts playlist order |
| [alexstyl_Memento-Calendar_169](Dataset/ReBL_Failed_Dataset/crash/alexstyl_Memento-Calendar_169) | alexstyl/Memento-Calendar | ✅ | ❌ | — | — | Custom-view date picker crash (ReBL failure set) |

**-> See the full per-bug breakdown for all 100 + 9 bugs in [RESULTS.md](RESULTS.md)**, including
per-tool verdicts, annotated screenshots, reproduction steps, and the legitimacy
audit notes for each tool.
