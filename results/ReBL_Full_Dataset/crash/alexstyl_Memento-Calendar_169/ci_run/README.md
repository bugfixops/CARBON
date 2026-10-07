# Memento#169: CARBON run on a CI emulator (October 2026)

A third CARBON run on Memento-Calendar#169, the paper's running example, made
to capture the screens for the paper's Figure 1. It is not part of the paper's
two campaigns (ReBL's benchmark, whose run is `../carbon_log.txt`, and the
ReBL failure set in `results/ReBL_Failed_Dataset/`), and it does not change
their results.

| | |
|---|---|
| Outcome | **not reproduced**: CARBON declared `fail` after 1,706 s; no crash of the app in logcat |
| APK | ReBL's benchmark APK (`../Memento-Calendar_169.apk`): versionName 3.6, target SDK 22 |
| Install | Android 14 refuses apps that target SDK < 23, so the harness repeated `adb install` with `--bypass-low-target-sdk-block` (see `harness.log`) |
| Device | GitHub-hosted runner, Android 14 (API 34) x86_64 emulator, Pixel 4 profile |
| Model | `gemini-2.5-pro`, temperature 0.3, 1,800 s budget, US$3 spend cap |
| LLM calls / cost | 29 calls, US$1.06 |
| Bug report | `bug_report.txt`, the same report as the ReBL-benchmark run (no notes on why ReBL failed) |
| Case | `alexstyl_Memento-Calendar_169`, defined in `baselines/harness/extra_cases.json` |

## Why it failed

As in the ReBL-benchmark run, the birthday dialog's view hierarchy has no node
for the day or month wheel (`carbon_log.txt`, every step: 0 scrollable
elements). On this device the hierarchy also lists the widgets of the
*Add birthday* dialog underneath, so CARBON drew their boxes over the wheels:
`#6` "Contact name" and `#7` "Birthday" (`screenshots/step_010_annotated.jpg`).
CARBON's first wheel gestures went to the centers of those boxes, (700, 1050)
and (750, 1250), which lie on the month wheel; later ones, at x = 540 and
x = 250, fell at the edge of the month wheel or beside the day wheel. The
month wheel turned (it reached February and March), but the day wheel moved
only once, from 7 to 8, in the last step, so the dialog never held
31 February. CARBON then judged the dialog unresponsive.

## Files

- `run.json`, `harness.log`: the harness record (status, install, logcat summary, token use).
- `carbon_log.txt`: CARBON's full transcript, with the element map of every step.
- `screenshots/`: every step's annotated screenshot (what the LLM saw) and the raw one, 540 px wide.
- `logcat.txt.gz`, `final.jpg`, `carbon_tokens.json`, `pip_freeze.txt`.
- `recording_segment_02.mp4`: the part of the screen recording that contains Figure 1's screen.
- `figure1_frame.png`: the full-resolution frame of that recording (74.7 s into the segment) used in Figure 1; it matches `screenshots/step_010_raw.jpg`.

Figure 1's logcat panel comes from the run that reproduced the bug on this APK
(`../carbon_log.txt`: after the SET tap, the step-19 prompt reports
`E AndroidRuntime: FATAL EXCEPTION: main`).
