# CARBON on gemini-2.5-pro — 100-Bug Gesture Benchmark

| | |
|---|---|
| Tool | CARBON |
| Model | `gemini-2.5-pro` |
| Cases tested | **100** |
| Reproduced | **88** |
| Not reproduced | **12** |

Counts are the audited ones — the figures published in the root
[`RESULTS.md`](../../RESULTS.md) and used in the paper. CARBON declared
**92** successes; the dual oracle confirmed **88**. The four rows below
marked "rejected on audit" are exactly that difference.

This document covers **CARBON only**. The same 100 bugs were also run
with ReBL, ReActDroid and AdbGPT, whose logs sit beside each bug in this
folder; on the same audit they reproduced 34, 5 and 4 respectively (from
nominal 50, 5 and 54), and the root [`RESULTS.md`](../../RESULTS.md) has
their per-bug and per-category tables.

Per-bug evidence sits in `<category>/<Owner>_<Repo>_<Issue> Tested`: the
bug report, one log per tool, and an annotated screenshot. Nine of the
twelve non-reproductions carry a trailing ` F` in the folder name; three
of the four audit rejections of a self-reported success
(`FossifyOrg_File-Manager_195`, `FossifyOrg_Calendar_1103`,
`libre-tube_LibreTube_8245`) were never renamed. The suffix is therefore
not an index of the failure set — the table below is.

## The 12 that failed

| Bug | Category | Why it failed | Log |
|---|---|---|---|
| `FossifyOrg_Gallery_584` | double tap | Opened every media file in Download, DCIM and Pictures; none crashed. The crash needs a specific malformed JPG that is not on the test image. | [carbon_log.txt](double_tap/FossifyOrg_Gallery_584%20Tested%20F/carbon_log.txt) |
| `LawnchairLauncher_lawnchair_4786` | double tap | Needs TalkBack's 3-finger tap to open the Actions menu. No available action produces that gesture; `long_click` opened a different menu instead. | [carbon_log.txt](double_tap/LawnchairLauncher_lawnchair_4786%20Tested%20F/carbon_log.txt) |
| `openboard-team_openboard_758` | double tap | Needs a screen-reader double-tap on `Navigate up`. A plain click navigated back correctly — the non-buggy behaviour — so the reported failure never appeared. | [carbon_log.txt](double_tap/openboard-team_openboard_758%20Tested%20F/carbon_log.txt) |
| `LawnchairLauncher_lawnchair_1247` | drag & drop | Crash is specific to TalkBack's `move` action. Ordinary drag-and-drop to a new page, into a folder, and creating a folder all completed without crashing. | [carbon_log.txt](drag_and_drop/LawnchairLauncher_lawnchair_1247%20Tested%20F/carbon_log.txt) |
| `FossifyOrg_File-Manager_195` | long press | Reached the reported state and reported success, but the symptom is a one-frame icon refresh that a screenshot cannot show. The claim was rejected on audit. | [carbon_log.txt](long_press/FossifyOrg_File-Manager_195%20Tested/carbon_log.txt) |
| `FossifyOrg_Clock_85` | orientation | The alarm always arrived as a notification, never the full-screen alarm UI that carries the swipe-to-snooze control, so snoozing in landscape could not be tested. | [carbon_log.txt](orientation/FossifyOrg_Clock_85%20Tested%20F/carbon_log.txt) |
| `ankidroid_Anki-Android_18529` | quick tap | Needs a tap landing while another element animates. Repeated `click`, `quick_tap` and `drag_and_drop` tries at different timings never interrupted the animation. | [carbon_log.txt](quick_tap/ankidroid_Anki-Android_18529%20Tested%20F/carbon_log.txt) |
| `ankidroid_Anki-Android_20789` | quick tap | The notification only appears after a completed AnkiWeb sync. Every sync path stopped at a mandatory login prompt and no credentials were available. | [carbon_log.txt](quick_tap/ankidroid_Anki-Android_20789%20Tested%20F/carbon_log.txt) |
| `FossifyOrg_Calendar_1103` | swipe | Read the day cell's content-description and inferred the missing announcement, but the reported symptom is what TalkBack speaks, which cannot be checked here. The claim was rejected on audit. | [carbon_log.txt](swipe/FossifyOrg_Calendar_1103%20Tested/carbon_log.txt) |
| `FossifyOrg_Clock_156` | swipe | The time picker would not accept a short duration, so no timer ever fired and the status-bar swipe that cancels the alarm could not be exercised. | [carbon_log.txt](swipe/FossifyOrg_Clock_156%20Tested%20F/carbon_log.txt) |
| `ankidroid_Anki-Android_14934` | swipe | Reached a state where card text was on screen but absent from the view hierarchy; the reported symptom is TalkBack's reading of the card, which cannot be checked here. The claim was rejected on audit. | [carbon_log.txt](swipe/ankidroid_Anki-Android_14934%20Tested%20F/carbon_log.txt) |
| `libre-tube_LibreTube_8245` | swipe | Performed the minimise-player trigger and reported success, but the symptom is animation smoothness, which cannot be measured here. The claim was rejected on audit. | [carbon_log.txt](swipe/libre-tube_LibreTube_8245%20Tested/carbon_log.txt) |

Failure to reproduce does not establish that a bug is fixed.
Each reason above says what blocked that run, not whether the bug
still exists upstream.

The same 100 bugs were also run with GPT-4o:
[`../CARBON_GPT4o_Dataset/RESULTS.md`](../CARBON_GPT4o_Dataset/RESULTS.md).
