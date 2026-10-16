# CARBON: Gemini 2.5 Pro vs GPT-4o — 100-Bug Dataset Comparison

Same CARBON pipeline, same 100-bug gesture-diverse benchmark, two different backing
LLMs. Gemini 2.5 Pro numbers are the audit-confirmed results from the main CARBON
results table. GPT-4o numbers come from this folder's [`RESULTS.md`](RESULTS.md), where
each bug's status is the `VERDICT:` line of its `carbon_gpt4o_log.txt`. That status
reflects the agent's own final verdict in the log, with the manual corrections described
in [`RESULTS.md`](RESULTS.md), not just whether the harness run finished without a
technical error.

Legend: ✅ success · ❌ failed.

## Overall

| Model | SUCCESS | FAILED | Success Rate |
|---|---|---|---|
| CARBON (Gemini 2.5 Pro) | 88 | 12 | 88.0% |
| CARBON (GPT-4o) | 81 | 19 | 81.0% |

| Agreement | Count |
|---|---|
| Both succeed | 78 |
| Both fail | 9 |
| Gemini succeeds, GPT-4o fails | 10 |
| GPT-4o succeeds, Gemini fails | 3 |

Of the 100 bugs, 78 agree on success and 9 agree on failure. The other 13 bugs diverge
between the two models.

## Bugs Gemini reproduced but GPT-4o did not (10)

| Category | Bug ID | Gemini | GPT-4o | Why GPT-4o failed |
|---|---|---|---|---|
| Quick Tap | anilbeesetti_nextplayer_1389 | ✅ | ❌ | Never reached the resume step: repeated the same `quick_tap` on one player control with no state change until the loop guard stopped the run. |
| Quick Tap | ankidroid_Anki-Android_19641 | ✅ | ❌ | Ran the full 60-minute limit without reaching the study screen: no card ever landed in the `test` deck (its counts stayed 0), so the answer-button step was unreachable. |
| Scroll | ankidroid_Anki-Android_5544 | ✅ | ❌ | Never got into the app: looped clicking `Search` on the device search screen while trying to find AnkiDroid. |
| Swipe | FossifyOrg_Calendar_153 | ✅ | ❌ | Never reached the calendar UI: alternated clicking the `Calendar` launcher icon and swiping until the loop guard stopped the run. |
| Swipe | FossifyOrg_Messages_80 | ✅ | ❌ | Loop guard stopped the run after three rounds of pressing `back` without the screen changing; the message thread was never reached. |
| Swipe | FossifyOrg_Notes_190 | ✅ | ❌ | Stuck on the theme dialog, bouncing between `Navigate up` and `OK`, and never reached the note list. |
| Swipe | iamrasel_lunar-launcher_82 | ✅ | ❌ | Spent the 30-minute limit on repeated swipe-up and `back` tries trying to get back to the launcher home screen, and was cut off before the repro step. |
| Swipe | LawnchairLauncher_lawnchair_4708 | ✅ | ❌ | Could not open Recents: repeated bottom-edge swipe-ups never switched view, so the ghost-app check never ran. |
| Swipe | OuterTune_OuterTune_1044 | ✅ | ❌ | Blocked by a new-folder dialog that never dismissed; repeated `OK` clicks left it on screen. |
| Swipe | you-apps_ClockYou_85 | ✅ | ❌ | Lost in the quick-settings panel, alternating swipe up and swipe down, and never returned to the app. |

7 of 10 are in Swipe.

## Bugs GPT-4o reproduced but Gemini did not (3)

| Category | Bug ID | Gemini | GPT-4o | Evidence |
|---|---|---|---|---|
| Orientation | FossifyOrg_Clock_85 | ❌ | ✅ | Agent rotated the device mid-alarm; alarm was silently dismissed instead of snoozing — matches the bug exactly. |
| Swipe | FossifyOrg_Calendar_1103 | ❌ | ✅ | Agent created an event and found that day's content-description in monthly view was only "25 September", with no mention of the event, which it reported as the missing TalkBack announcement. |
| Swipe | FossifyOrg_Clock_156 | ❌ | ✅ | Agent tapped the timer notification body; timer was left un-reset at 00:00 — matches the bug exactly. |

## Bugs neither model reproduced (9)

| Category | Bug ID | Gemini | GPT-4o |
|---|---|---|---|
| Double Tap | openboard-team_openboard_758 | ❌ | ❌ |
| Double Tap | FossifyOrg_Gallery_584 | ❌ | ❌ |
| Double Tap | LawnchairLauncher_lawnchair_4786 | ❌ | ❌ |
| Drag & Drop | LawnchairLauncher_lawnchair_1247 | ❌ | ❌ |
| Long Press | FossifyOrg_File-Manager_195 | ❌ | ❌ |
| Quick Tap | ankidroid_Anki-Android_18529 | ❌ | ❌ |
| Quick Tap | ankidroid_Anki-Android_20789 | ❌ | ❌ |
| Swipe | ankidroid_Anki-Android_14934 | ❌ | ❌ |
| Swipe | libre-tube_LibreTube_8245 | ❌ | ❌ |

Four of these depend on TalkBack: `LawnchairLauncher_lawnchair_4786`,
`LawnchairLauncher_lawnchair_1247`, `openboard-team_openboard_758` and
`ankidroid_Anki-Android_14934`. For the two Lawnchair bugs, both models' agents describe
the same root limitation (no available action produces the TalkBack 3-finger tap or
`move` action the bug needs) — a genuine capability gap rather than a model-specific miss.

## Notes

- Scope is strictly the 100-bug main dataset. The 9-bug ReBL Failure Challenge Set
  is excluded since no GPT-4o run exists for it in `results/carbon-test-gpt-4o`.
- Other tools (ReBL, ReActDroid, AdbGPT) are out of scope for this comparison by
  request; this file compares CARBON against itself across the two backing LLMs
  only.
