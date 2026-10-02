# CARBON: Gemini 2.5 Pro vs GPT-4o — 100-Bug Dataset Comparison

Same CARBON pipeline, same 100-bug gesture-diverse benchmark, two different backing
LLMs. Gemini 2.5 Pro numbers are the audit-confirmed results from the main CARBON
results table. GPT-4o numbers come from `TEST_RESULTS_SUMMARY.md`, resolved per bug
(a bug's log may have multiple run attempts; success is used if any attempt
succeeded, otherwise the most complete failed attempt is used). Status reflects the
agent's own final verdict in the log transcript, not just whether the harness run
finished without a technical error.

Legend: ✅ success · ❌ failed.

## Overall

| Model | SUCCESS | FAILED | Success Rate |
|---|---|---|---|
| CARBON (Gemini 2.5 Pro) | 88 | 12 | 88.0% |
| CARBON (GPT-4o) | 81 | 19 | 81.0% |

| Agreement | Count |
|---|---|
| Both succeed | 79 |
| Both fail | 10 |
| Gemini succeeds, GPT-4o fails | 9 |
| GPT-4o succeeds, Gemini fails | 2 |

Of the 100 bugs, 79 agree on success and 10 agree on failure. Only 11 bugs diverge
between the two models.

## Bugs Gemini reproduced but GPT-4o did not (9)

| Category | Bug ID | Gemini | GPT-4o |
|---|---|---|---|
| Quick Tap | anilbeesetti_nextplayer_1389 | ✅ | ❌ |
| Quick Tap | ankidroid_Anki-Android_19641 | ✅ | ❌ |
| Scroll | ankidroid_Anki-Android_5544 | ✅ | ❌ |
| Swipe | FossifyOrg_Messages_80 | ✅ | ❌ |
| Swipe | FossifyOrg_Notes_190 | ✅ | ❌ |
| Swipe | iamrasel_lunar-launcher_82 | ✅ | ❌ |
| Swipe | LawnchairLauncher_lawnchair_4708 | ✅ | ❌ |
| Swipe | OuterTune_OuterTune_1044 | ✅ | ❌ |
| Swipe | you-apps_ClockYou_85 | ✅ | ❌ |

6 of 9 are in Swipe.

## Bugs GPT-4o reproduced but Gemini did not (2)

| Category | Bug ID | Gemini | GPT-4o | Evidence |
|---|---|---|---|---|
| Orientation | FossifyOrg_Clock_85 | ❌ | ✅ | Agent rotated the device mid-alarm; alarm was silently dismissed instead of snoozing — matches the bug exactly. |
| Swipe | FossifyOrg_Clock_156 | ❌ | ✅ | Agent tapped the timer notification body; timer was left un-reset at 00:00 — matches the bug exactly. |

## Bugs neither model reproduced (10)

| Category | Bug ID | Gemini | GPT-4o |
|---|---|---|---|
| Double Tap | openboard-team_openboard_758 | ❌ | ❌ |
| Double Tap | FossifyOrg_Gallery_584 | ❌ | ❌ |
| Double Tap | LawnchairLauncher_lawnchair_4786 | ❌ | ❌ |
| Drag & Drop | LawnchairLauncher_lawnchair_1247 | ❌ | ❌ |
| Long Press | FossifyOrg_File-Manager_195 | ❌ | ❌ |
| Quick Tap | ankidroid_Anki-Android_18529 | ❌ | ❌ |
| Quick Tap | ankidroid_Anki-Android_20789 | ❌ | ❌ |
| Swipe | FossifyOrg_Calendar_1103 | ❌ | ❌ |
| Swipe | ankidroid_Anki-Android_14934 | ❌ | ❌ |
| Swipe | libre-tube_LibreTube_8245 | ❌ | ❌ |

Four of these are TalkBack-accessibility-gesture bugs where both models' agents
describe the same root limitation (no way to simulate a 3-finger TalkBack tap) — a
genuine capability gap rather than a model-specific miss.

## Notes

- Scope is strictly the 100-bug main dataset. The 9-bug ReBL Failure Challenge Set
  is excluded since no GPT-4o run exists for it in `Results-retest-merge`.
- Other tools (ReBL, ReActDroid, AdbGPT) are out of scope for this comparison by
  request; this file compares CARBON against itself across the two backing LLMs
  only.
