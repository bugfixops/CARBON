# CARBON on GPT-4o — 100-Bug Gesture Benchmark

| | |
|---|---|
| Tool | CARBON |
| Model | `GPT-4o` |
| Cases tested | **100** |
| Reproduced | **81** |
| Not reproduced | **19** |

The same 100 bug reports as the `gemini-2.5-pro` campaign in the root
[`RESULTS.md`](../../RESULTS.md), re-run with GPT-4o as the backing
model. Each bug's transcript sits beside it in this folder as
`carbon_gpt4o_log.txt`.

Each bug here is resolved from the agent's own final verdict in its
transcript, plus manual loop-abort and false-positive corrections (the
rows reading "Rejected on review"). This is **not** the six-criterion
legitimacy audit that produces the `gemini-2.5-pro` figure of 88, so 81
against 88 is not a like-for-like model delta.

## The 19 that failed

| Bug | Category | Why it failed | Log |
|---|---|---|---|
| `FossifyOrg_Gallery_584` | double tap | Ran a different sequence from the one the report specifies, so the reported trigger was never performed. | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_584%20Tested%20F/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4786` | double tap | Could not produce the TalkBack 3-finger gesture the bug requires. | [carbon_gpt4o_log.txt](double_tap/LawnchairLauncher_lawnchair_4786%20Tested%20F/carbon_gpt4o_log.txt) |
| `openboard-team_openboard_758` | double tap | TalkBack was never enabled, so the screen-reader double-tap was never performed; the agent clicked `Navigate up`, saw it navigate correctly — the non-buggy behaviour — and called it a reproduction. Rejected on review. | [carbon_gpt4o_log.txt](double_tap/openboard-team_openboard_758%20Tested%20F/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_1247` | drag & drop | Could not produce the TalkBack `move` action the crash requires. | [carbon_gpt4o_log.txt](drag_and_drop/LawnchairLauncher_lawnchair_1247%20Tested%20F/carbon_gpt4o_log.txt) |
| `FossifyOrg_File-Manager_195` | long press | Claimed success without ever observing the icon refresh it set out to check. Rejected on review. | [carbon_gpt4o_log.txt](long_press/FossifyOrg_File-Manager_195%20Tested/carbon_gpt4o_log.txt) |
| `anilbeesetti_nextplayer_1389` | quick tap | Never reached the resume step: repeated the same `quick_tap` on one player control with no state change until the loop guard stopped the run. | [carbon_gpt4o_log.txt](quick_tap/anilbeesetti_nextplayer_1389%20Tested/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_18529` | quick tap | Never performed the mid-animation interaction this race needs. It tapped `+` on an empty deck list, hit an unrelated first-run ANR, and reported that as the bug. Rejected on review. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_18529%20Tested%20F/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_19641` | quick tap | Ran the full 60-minute limit without reaching the study screen: no card ever landed in the `test` deck (its counts stayed 0), so the answer-button step was unreachable. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_19641%20Tested/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_20789` | quick tap | Blocked by a login wall before the AnkiWeb sync the notification depends on. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_20789%20Tested%20F/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_5544` | scroll | Never got into the app: looped clicking `Search` on the device search screen while trying to find AnkiDroid. | [carbon_gpt4o_log.txt](scroll/ankidroid_Anki-Android_5544%20Tested/carbon_gpt4o_log.txt) |
| `FossifyOrg_Calendar_153` | swipe | Never reached the calendar UI: alternated clicking the `Calendar` launcher icon and swiping until the loop guard stopped the run. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Calendar_153%20Tested/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_80` | swipe | Loop guard stopped the run after three rounds of pressing `back` without the screen changing; the message thread was never reached. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Messages_80%20Tested/carbon_gpt4o_log.txt) |
| `FossifyOrg_Notes_190` | swipe | Stuck on the theme dialog, bouncing between `Navigate up` and `OK`, and never reached the note list. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Notes_190%20Tested/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4708` | swipe | Could not open Recents: repeated bottom-edge swipe-ups never switched view, so the ghost-app check never ran. | [carbon_gpt4o_log.txt](swipe/LawnchairLauncher_lawnchair_4708%20Tested/carbon_gpt4o_log.txt) |
| `OuterTune_OuterTune_1044` | swipe | Blocked by a new-folder dialog that never dismissed; repeated `OK` clicks left it on screen. | [carbon_gpt4o_log.txt](swipe/OuterTune_OuterTune_1044%20Tested/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_14934` | swipe | Hit the 15-minute cap while looping through deck creation and sync dialogs; the card-study screen was never reached. | [carbon_gpt4o_log.txt](swipe/ankidroid_Anki-Android_14934%20Tested%20F/carbon_gpt4o_log.txt) |
| `iamrasel_lunar-launcher_82` | swipe | Spent the 30-minute limit on repeated swipe-up and `back` tries trying to get back to the launcher home screen, and was cut off before the repro step. | [carbon_gpt4o_log.txt](swipe/iamrasel_lunar-launcher_82%20Tested/carbon_gpt4o_log.txt) |
| `libre-tube_LibreTube_8245` | swipe | No video content ever loaded, so the playback step the bug needs was never reached. | [carbon_gpt4o_log.txt](swipe/libre-tube_LibreTube_8245%20Tested/carbon_gpt4o_log.txt) |
| `you-apps_ClockYou_85` | swipe | Lost in the quick-settings panel, alternating swipe up and swipe down, and never returned to the app. | [carbon_gpt4o_log.txt](swipe/you-apps_ClockYou_85%20Tested/carbon_gpt4o_log.txt) |

Failure to reproduce does not establish that a bug is fixed.
Each reason above says what blocked that run, not whether the bug
still exists upstream.

Per-bug comparison between the two models:
[`../CARBON_gemini-2.5-pro_vs_gpt-4o.md`](../CARBON_gemini-2.5-pro_vs_gpt-4o.md).
Its 88 and 81 totals match this page, but its agreement table does not
reconcile with the per-case verdicts: `FossifyOrg_Calendar_1103` is filed
under "neither model reproduced" although GPT-4o reproduced it, and
`FossifyOrg_Calendar_153` — a GPT-4o failure and a Gemini success — is in
no divergence table. The per-case counts are 78 both-succeed, 9 both-fail,
10 Gemini-only, 3 GPT-4o-only, so 13 bugs diverge rather than 11. That
document is kept unedited by request; read its 2×2 with this correction.

Folder layout: [`README.md`](README.md).
