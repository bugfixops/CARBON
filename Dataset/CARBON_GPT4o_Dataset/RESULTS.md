# CARBON on GPT-4o — 100-Bug Gesture Benchmark

| | |
|---|---|
| Tool | CARBON |
| Model | `GPT-4o` |
| Cases tested | **100** |
| Reproduced | **81** (81.0%) |
| Not reproduced | **19** |
| Runs | 188 across 100 cases |
| Dates | 2026-09-20, 2026-09-22, 2026-09-25 (from the run log filenames) |

The same 100 bug reports as the `gemini-2.5-pro` campaign in the root
[`RESULTS.md`](../../RESULTS.md), re-run with GPT-4o as the backing
model. Each bug's transcript sits beside it in this folder as
`carbon_gpt4o_log.txt`.

## How the 81 is resolved

**This campaign is best-of-N, and the `gemini-2.5-pro` 88 is not.** The
100 cases were run 188 times in total — most cases more than once — and
each case is resolved to one representative run by this rule:

1. Prefer a **SUCCESS** run (the most recent, if several succeeded).
2. Otherwise the **FAILED** run with the fullest log (largest file, most
   recent as tiebreak).
3. Otherwise the most complete **INCOMPLETE** (truncated) log.

So a case counts as reproduced if **any** of its attempts reported
success. The per-case table below gives each case's attempt count and the
run that was selected; the 188 source runs are in
[`../../Results-retest-merge/`](../../Results-retest-merge/).

Within the selected run the verdict is the agent's own final verdict in
its transcript, plus manual loop-abort and false-positive corrections.
This is **not** the six-criterion legitimacy audit that produces the
`gemini-2.5-pro` figure of 88. Because of both differences — best-of-N
against single-run, and no legitimacy audit — 81 against 88 is not a
like-for-like model delta.

**Where each failure verdict is recorded.** 13 of the 19 are marked as
failures inside their own selected log — a
`[CARBON RETEST -- MANUAL VERDICT] result: FAIL` block, a
`FAILED: exceeded ... time limit` line, or a non-`completed`
`FINAL status=`. The other **6 carry no failure marker in the log**:
`FossifyOrg_Gallery_584`, `LawnchairLauncher_lawnchair_4786`,
`LawnchairLauncher_lawnchair_1247`, `ankidroid_Anki-Android_20789` and
`libre-tube_LibreTube_8245` all end `FINAL status=completed`, and
`FossifyOrg_File-Manager_195` ends with no status line at all. For those
6 the reason in the table below is the only record, so reading the log
alone would suggest a clean finish. Three rows additionally say "Rejected
on review", which is a narrower thing — the agent asserted it had
reproduced the bug and that assertion was overturned.

## Per category

| Category | Cases | Reproduced | Not reproduced |
|---|---:|---:|---:|
| double tap | 21 | 18 | 3 |
| drag and drop | 9 | 8 | 1 |
| long press | 9 | 8 | 1 |
| orientation | 6 | 6 | 0 |
| pinch zoom | 12 | 12 | 0 |
| quick tap | 7 | 3 | 4 |
| scroll | 6 | 5 | 1 |
| swipe | 30 | 21 | 9 |
| **Total** | **100** | **81** | **19** |

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
**Its agreement table does not reconcile with the per-case verdicts.** Two
cases are misfiled: `FossifyOrg_Calendar_1103` is listed under "Bugs neither
model reproduced" although GPT-4o reproduced it, and `FossifyOrg_Calendar_153`
— a GPT-4o failure and a Gemini success — appears in no divergence table. The
corrected cells are **78** both succeed, **9** both fail, **10** Gemini only,
**3** GPT-4o only, so **13** bugs diverge — not the 79 both succeed, 10 both
fail, 9 Gemini only, 2 GPT-4o only and "only 11 bugs diverge" that it
publishes. The 88 and 81 totals are unaffected. That document
is kept unedited by request; read its 2×2 with this correction.

Folder layout: [`README.md`](README.md).

## Appendix — all 100 cases

Every case with its resolved verdict, how many runs it had, and which run
was selected by the rule above. Verdicts are the ones published for this
campaign; no case is re-classified here.

How the Detail column was derived:

- Classification comes from log content, never from the folder-name suffix.
- `[run_retest]`-tagged logs are read from their `FINAL status=` line:
  `completed` is a success; `failed(timeout)`, `failed(loop)`,
  `error(returncode=...)` and `apk_unavailable` are failures; a missing
  line means incomplete or truncated.
- `[run_dataset]`-tagged logs (the original pre-retest runs) carry no
  status line. Failure is marked by `[run_dataset] FAILED: exceeded 900s
  (15 min) time limit`. Absent that, a case is inferred successful only
  if it reaches a `token usage` summary **and** is not overturned by a
  `[CARBON RETEST -- MANUAL VERDICT] result: FAIL` block. **13 cases had
  an initial inferred-success verdict manually overturned on review.**
- 5 untagged logs, all from 2026-09-20 and 2026-09-22, predate the tagging
  convention and died on repeated OpenAI API errors before any terminal
  marker; they are treated as incomplete.

### double_tap

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_1035 Tested` | ✅ SUCCESS | 1 | [20260920_175151_600.log](../../Results-retest-merge/double_tap/FossifyOrg_Calendar_1035%20Tested/20260920_175151_600.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Calendar_273 Tested` | ✅ SUCCESS | 1 | [20260920_181251_569.log](../../Results-retest-merge/double_tap/FossifyOrg_Calendar_273%20Tested/20260920_181251_569.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_363 Tested` | ✅ SUCCESS | 1 | [20260920_181254_572.log](../../Results-retest-merge/double_tap/FossifyOrg_Gallery_363%20Tested/20260920_181254_572.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_584 Tested F` | ❌ FAILED | 3 | [20260925_024032_169.log](../../Results-retest-merge/double_tap/FossifyOrg_Gallery_584%20Tested%20F/20260925_024032_169.log) | agent did not follow the reported repro steps, substituting its own scenario instead |
| `FossifyOrg_Gallery_678 Tested` | ✅ SUCCESS | 2 | [20260922_200151_551.log](../../Results-retest-merge/double_tap/FossifyOrg_Gallery_678%20Tested/20260922_200151_551.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_846 Tested` | ✅ SUCCESS | 1 | [20260920_181307_962.log](../../Results-retest-merge/double_tap/FossifyOrg_Gallery_846%20Tested/20260920_181307_962.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_847 Tested` | ✅ SUCCESS | 1 | [20260920_181309_561.log](../../Results-retest-merge/double_tap/FossifyOrg_Gallery_847%20Tested/20260920_181309_561.log) | inferred (no FAILED line, token usage present) |
| `LawnchairLauncher_lawnchair_2910 Tested` | ✅ SUCCESS | 1 | [20260920_181610_327.log](../../Results-retest-merge/double_tap/LawnchairLauncher_lawnchair_2910%20Tested/20260920_181610_327.log) | inferred (no FAILED line, token usage present) |
| `LawnchairLauncher_lawnchair_4125 Tested` | ✅ SUCCESS | 2 | [20260925_024149_700.log](../../Results-retest-merge/double_tap/LawnchairLauncher_lawnchair_4125%20Tested/20260925_024149_700.log) | completed |
| `LawnchairLauncher_lawnchair_4786 Tested F` | ❌ FAILED | 2 | [20260925_024037_786.log](../../Results-retest-merge/double_tap/LawnchairLauncher_lawnchair_4786%20Tested%20F/20260925_024037_786.log) | agent could not simulate the TalkBack 3-finger gesture required to trigger the bug |
| `Pool-Of-Tears_GreenStash_170 Tested` | ✅ SUCCESS | 2 | [20260925_023930_226.log](../../Results-retest-merge/double_tap/Pool-Of-Tears_GreenStash_170%20Tested/20260925_023930_226.log) | completed |
| `TeamNewPipe_NewPipe_10750 Tested` | ✅ SUCCESS | 3 | [20260925_023941_774.log](../../Results-retest-merge/double_tap/TeamNewPipe_NewPipe_10750%20Tested/20260925_023941_774.log) | completed |
| `TeamNewPipe_NewPipe_8338 Tested` | ✅ SUCCESS | 1 | [20260920_183520_067.log](../../Results-retest-merge/double_tap/TeamNewPipe_NewPipe_8338%20Tested/20260920_183520_067.log) | inferred (no FAILED line, token usage present) |
| `abdallahmehiz_mpvKt_184 Tested` | ✅ SUCCESS | 1 | [20260920_174647_056.log](../../Results-retest-merge/double_tap/abdallahmehiz_mpvKt_184%20Tested/20260920_174647_056.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_17393 Tested` | ✅ SUCCESS | 2 | [20260925_023937_155.log](../../Results-retest-merge/double_tap/ankidroid_Anki-Android_17393%20Tested/20260925_023937_155.log) | completed |
| `cromaguy_Rhythm_281 Tested` | ✅ SUCCESS | 1 | [20260920_174653_058.log](../../Results-retest-merge/double_tap/cromaguy_Rhythm_281%20Tested/20260920_174653_058.log) | inferred (no FAILED line, token usage present) |
| `fast4x_RiMusic_1152 Tested` | ✅ SUCCESS | 2 | [20260925_023924_627.log](../../Results-retest-merge/double_tap/fast4x_RiMusic_1152%20Tested/20260925_023924_627.log) | completed |
| `gsantner_markor_2746 Tested` | ✅ SUCCESS | 4 | [20260925_053933_979.log](../../Results-retest-merge/double_tap/gsantner_markor_2746%20Tested/20260925_053933_979.log) | completed |
| `openboard-team_openboard_613 Tested` | ✅ SUCCESS | 2 | [20260925_023942_136.log](../../Results-retest-merge/double_tap/openboard-team_openboard_613%20Tested/20260925_023942_136.log) | completed |
| `openboard-team_openboard_758 Tested F` | ❌ FAILED | 1 | [20260920_182718_163.log](../../Results-retest-merge/double_tap/openboard-team_openboard_758%20Tested%20F/20260920_182718_163.log) | manual override (false-positive correction) |
| `syt0r_Kanji-Dojo_291 Tested` | ✅ SUCCESS | 1 | [20260920_183205_040.log](../../Results-retest-merge/double_tap/syt0r_Kanji-Dojo_291%20Tested/20260920_183205_040.log) | inferred (no FAILED line, token usage present) |

### drag_and_drop

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Launcher_304 Tested` | ✅ SUCCESS | 2 | [20260925_023932_666.log](../../Results-retest-merge/drag_and_drop/FossifyOrg_Launcher_304%20Tested/20260925_023932_666.log) | completed |
| `FossifyOrg_Notes_59 Tested` | ✅ SUCCESS | 2 | [20260925_023938_347.log](../../Results-retest-merge/drag_and_drop/FossifyOrg_Notes_59%20Tested/20260925_023938_347.log) | completed |
| `LawnchairLauncher_lawnchair_1247 Tested F` | ❌ FAILED | 2 | [20260925_030228_727.log](../../Results-retest-merge/drag_and_drop/LawnchairLauncher_lawnchair_1247%20Tested%20F/20260925_030228_727.log) | agent could not simulate the TalkBack move action required to trigger the bug |
| `LawnchairLauncher_lawnchair_4320 Tested` | ✅ SUCCESS | 2 | [20260925_024715_703.log](../../Results-retest-merge/drag_and_drop/LawnchairLauncher_lawnchair_4320%20Tested/20260925_024715_703.log) | completed |
| `MetrolistGroup_Metrolist_3227 Tested` | ✅ SUCCESS | 4 | [20260925_073514_550.log](../../Results-retest-merge/drag_and_drop/MetrolistGroup_Metrolist_3227%20Tested/20260925_073514_550.log) | completed |
| `MetrolistGroup_Metrolist_3561 Tested` | ✅ SUCCESS | 1 | [20260920_185447_163.log](../../Results-retest-merge/drag_and_drop/MetrolistGroup_Metrolist_3561%20Tested/20260920_185447_163.log) | inferred (no FAILED line, token usage present) |
| `NeoApplications_Neo-Launcher_130 Tested` | ✅ SUCCESS | 4 | [20260925_073531_255.log](../../Results-retest-merge/drag_and_drop/NeoApplications_Neo-Launcher_130%20Tested/20260925_073531_255.log) | completed |
| `breezy-weather_breezy-weather_2159 Tested` | ✅ SUCCESS | 2 | [20260925_024931_925.log](../../Results-retest-merge/drag_and_drop/breezy-weather_breezy-weather_2159%20Tested/20260925_024931_925.log) | completed |
| `fcitx5-android_fcitx5-android_841 Tested` | ✅ SUCCESS | 4 | [20260925_073453_758.log](../../Results-retest-merge/drag_and_drop/fcitx5-android_fcitx5-android_841%20Tested/20260925_073453_758.log) | completed |

### long_press

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `Anthonyy232_Paperize_325 Tested` | ✅ SUCCESS | 2 | [20260925_024811_765.log](../../Results-retest-merge/long_press/Anthonyy232_Paperize_325%20Tested/20260925_024811_765.log) | completed |
| `Crustack_NotallyX_570 Tested` | ✅ SUCCESS | 4 | [20260925_073535_687.log](../../Results-retest-merge/long_press/Crustack_NotallyX_570%20Tested/20260925_073535_687.log) | completed |
| `FossifyOrg_File-Manager_195 Tested` | ❌ FAILED | 1 | [20260920_191238_869.log](../../Results-retest-merge/long_press/FossifyOrg_File-Manager_195%20Tested/20260920_191238_869.log) | agent claimed success without verifying the icon behavior it set out to check |
| `FossifyOrg_Launcher_198 Tested` | ✅ SUCCESS | 2 | [20260925_025316_313.log](../../Results-retest-merge/long_press/FossifyOrg_Launcher_198%20Tested/20260925_025316_313.log) | completed |
| `FossifyOrg_Messages_359 Tested` | ✅ SUCCESS | 1 | [20260920_191432_689.log](../../Results-retest-merge/long_press/FossifyOrg_Messages_359%20Tested/20260920_191432_689.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Messages_416 Tested` | ✅ SUCCESS | 2 | [20260925_025039_531.log](../../Results-retest-merge/long_press/FossifyOrg_Messages_416%20Tested/20260925_025039_531.log) | completed |
| `FossifyOrg_Messages_641 Tested` | ✅ SUCCESS | 7 | [20260925_111906_756.log](../../Results-retest-merge/long_press/FossifyOrg_Messages_641%20Tested/20260925_111906_756.log) | completed |
| `breezy-weather_breezy-weather_1639 Tested` | ✅ SUCCESS | 2 | [20260925_025659_590.log](../../Results-retest-merge/long_press/breezy-weather_breezy-weather_1639%20Tested/20260925_025659_590.log) | completed |
| `espresso3389_methings_34 Tested` | ✅ SUCCESS | 2 | [20260925_031355_254.log](../../Results-retest-merge/long_press/espresso3389_methings_34%20Tested/20260925_031355_254.log) | completed |

### orientation

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_1042 Tested` | ✅ SUCCESS | 1 | [20260920_192807_181.log](../../Results-retest-merge/orientation/FossifyOrg_Calendar_1042%20Tested/20260920_192807_181.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Camera_91 Tested` | ✅ SUCCESS | 1 | [20260920_193008_183.log](../../Results-retest-merge/orientation/FossifyOrg_Camera_91%20Tested/20260920_193008_183.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Clock_85 Tested F` | ✅ SUCCESS | 5 | [20260925_111843_437.log](../../Results-retest-merge/orientation/FossifyOrg_Clock_85%20Tested%20F/20260925_111843_437.log) | completed |
| `FossifyOrg_Contacts_197 Tested` | ✅ SUCCESS | 1 | [20260920_193309_421.log](../../Results-retest-merge/orientation/FossifyOrg_Contacts_197%20Tested/20260920_193309_421.log) | inferred (no FAILED line, token usage present) |
| `Waboodoo_HTTP-Shortcuts_262 Tested` | ✅ SUCCESS | 1 | [20260920_193316_693.log](../../Results-retest-merge/orientation/Waboodoo_HTTP-Shortcuts_262%20Tested/20260920_193316_693.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_16410 Tested` | ✅ SUCCESS | 1 | [20260920_192536_330.log](../../Results-retest-merge/orientation/ankidroid_Anki-Android_16410%20Tested/20260920_192536_330.log) | inferred (no FAILED line, token usage present) |

### pinch_zoom

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_621 Tested` | ✅ SUCCESS | 2 | [20260925_025142_237.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Calendar_621%20Tested/20260925_025142_237.log) | completed |
| `FossifyOrg_Camera_23 Tested` | ✅ SUCCESS | 2 | [20260925_032220_040.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Camera_23%20Tested/20260925_032220_040.log) | completed |
| `FossifyOrg_Gallery_289 Tested` | ✅ SUCCESS | 1 | [20260920_194358_203.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Gallery_289%20Tested/20260920_194358_203.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_642 Tested` | ✅ SUCCESS | 1 | [20260920_195347_452.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Gallery_642%20Tested/20260920_195347_452.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_728 Tested` | ✅ SUCCESS | 1 | [20260922_203349_078.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Gallery_728%20Tested/20260922_203349_078.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Paint_125 Tested` | ✅ SUCCESS | 1 | [20260922_203703_465.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Paint_125%20Tested/20260922_203703_465.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Paint_25 Tested` | ✅ SUCCESS | 1 | [20260922_203843_036.log](../../Results-retest-merge/pinch_zoom/FossifyOrg_Paint_25%20Tested/20260922_203843_036.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_16135 Tested` | ✅ SUCCESS | 1 | [20260920_193602_254.log](../../Results-retest-merge/pinch_zoom/ankidroid_Anki-Android_16135%20Tested/20260920_193602_254.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_17667 Tested` | ✅ SUCCESS | 2 | [20260922_203347_838.log](../../Results-retest-merge/pinch_zoom/ankidroid_Anki-Android_17667%20Tested/20260922_203347_838.log) | inferred (no FAILED line, token usage present) |
| `saber-notes_saber_192 Tested` | ✅ SUCCESS | 1 | [20260922_204005_304.log](../../Results-retest-merge/pinch_zoom/saber-notes_saber_192%20Tested/20260922_204005_304.log) | inferred (no FAILED line, token usage present) |
| `streetcomplete_StreetComplete_6068 Tested` | ✅ SUCCESS | 1 | [20260922_204014_086.log](../../Results-retest-merge/pinch_zoom/streetcomplete_StreetComplete_6068%20Tested/20260922_204014_086.log) | inferred (no FAILED line, token usage present) |
| `you-apps_WallYou_216 Tested` | ✅ SUCCESS | 1 | [20260922_204059_713.log](../../Results-retest-merge/pinch_zoom/you-apps_WallYou_216%20Tested/20260922_204059_713.log) | inferred (no FAILED line, token usage present) |

### quick_tap

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `LawnchairLauncher_lawnchair_5540 Tested` | ✅ SUCCESS | 1 | [20260922_204821_633.log](../../Results-retest-merge/quick_tap/LawnchairLauncher_lawnchair_5540%20Tested/20260922_204821_633.log) | inferred (no FAILED line, token usage present) |
| `anilbeesetti_nextplayer_1389 Tested` | ❌ FAILED | 1 | [20260922_204211_248.log](../../Results-retest-merge/quick_tap/anilbeesetti_nextplayer_1389%20Tested/20260922_204211_248.log) | manual override (loop-abort) |
| `ankidroid_Anki-Android_18529 Tested F` | ❌ FAILED | 1 | [20260922_204343_086.log](../../Results-retest-merge/quick_tap/ankidroid_Anki-Android_18529%20Tested%20F/20260922_204343_086.log) | manual override (false-positive correction) |
| `ankidroid_Anki-Android_19641 Tested` | ❌ FAILED | 4 | [20260925_073508_329.log](../../Results-retest-merge/quick_tap/ankidroid_Anki-Android_19641%20Tested/20260925_073508_329.log) | failed(timeout) |
| `ankidroid_Anki-Android_20789 Tested F` | ❌ FAILED | 3 | [20260925_044159_713.log](../../Results-retest-merge/quick_tap/ankidroid_Anki-Android_20789%20Tested%20F/20260925_044159_713.log) | agent was blocked by a login/permission wall before reaching the sync step needed to trigger the bug |
| `ankidroid_Anki-Android_7138 Tested` | ✅ SUCCESS | 4 | [20260925_073519_517.log](../../Results-retest-merge/quick_tap/ankidroid_Anki-Android_7138%20Tested/20260925_073519_517.log) | completed |
| `yairm210_Unciv_13517 Tested` | ✅ SUCCESS | 2 | [20260925_025156_199.log](../../Results-retest-merge/quick_tap/yairm210_Unciv_13517%20Tested/20260925_025156_199.log) | completed |

### scroll

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `Anthonyy232_Paperize_426 Tested` | ✅ SUCCESS | 1 | [20260922_210327_443.log](../../Results-retest-merge/scroll/Anthonyy232_Paperize_426%20Tested/20260922_210327_443.log) | inferred (no FAILED line, token usage present) |
| `Fandroid745_Open-notes_15 Tested` | ✅ SUCCESS | 2 | [20260925_034709_490.log](../../Results-retest-merge/scroll/Fandroid745_Open-notes_15%20Tested/20260925_034709_490.log) | completed |
| `FossifyOrg_File-Manager_136 Tested` | ✅ SUCCESS | 2 | [20260925_034849_968.log](../../Results-retest-merge/scroll/FossifyOrg_File-Manager_136%20Tested/20260925_034849_968.log) | completed |
| `ankidroid_Anki-Android_5512 Tested` | ✅ SUCCESS | 1 | [20260922_210214_396.log](../../Results-retest-merge/scroll/ankidroid_Anki-Android_5512%20Tested/20260922_210214_396.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_5544 Tested` | ❌ FAILED | 1 | [20260922_210314_563.log](../../Results-retest-merge/scroll/ankidroid_Anki-Android_5544%20Tested/20260922_210314_563.log) | manual override (loop-abort) |
| `netmackan_ATimeTracker_124 Tested` | ✅ SUCCESS | 1 | [20260922_210902_839.log](../../Results-retest-merge/scroll/netmackan_ATimeTracker_124%20Tested/20260922_210902_839.log) | inferred (no FAILED line, token usage present) |

### swipe

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `A-EDev_Flow_27 Tested` | ✅ SUCCESS | 3 | [20260925_044241_668.log](../../Results-retest-merge/swipe/A-EDev_Flow_27%20Tested/20260925_044241_668.log) | completed |
| `A-EDev_Flow_284 Tested` | ✅ SUCCESS | 1 | [20260922_211655_125.log](../../Results-retest-merge/swipe/A-EDev_Flow_284%20Tested/20260922_211655_125.log) | inferred (no FAILED line, token usage present) |
| `CodeWorksCreativeHub_mLauncher_809 Tested` | ✅ SUCCESS | 2 | [20260925_032843_397.log](../../Results-retest-merge/swipe/CodeWorksCreativeHub_mLauncher_809%20Tested/20260925_032843_397.log) | completed |
| `Droid-ify_client_238 Tested` | ✅ SUCCESS | 2 | [20260925_034235_880.log](../../Results-retest-merge/swipe/Droid-ify_client_238%20Tested/20260925_034235_880.log) | completed |
| `Droid-ify_client_583 Tested` | ✅ SUCCESS | 2 | [20260925_025449_452.log](../../Results-retest-merge/swipe/Droid-ify_client_583%20Tested/20260925_025449_452.log) | completed |
| `FossifyOrg_Calendar_1103 Tested` | ✅ SUCCESS | 2 | [20260925_033155_885.log](../../Results-retest-merge/swipe/FossifyOrg_Calendar_1103%20Tested/20260925_033155_885.log) | completed |
| `FossifyOrg_Calendar_153 Tested` | ❌ FAILED | 1 | [20260922_215528_173.log](../../Results-retest-merge/swipe/FossifyOrg_Calendar_153%20Tested/20260922_215528_173.log) | manual override (loop-abort) |
| `FossifyOrg_Clock_156 Tested F` | ✅ SUCCESS | 2 | [20260925_032456_487.log](../../Results-retest-merge/swipe/FossifyOrg_Clock_156%20Tested%20F/20260925_032456_487.log) | completed |
| `FossifyOrg_Gallery_237 Tested` | ✅ SUCCESS | 2 | [20260925_035112_847.log](../../Results-retest-merge/swipe/FossifyOrg_Gallery_237%20Tested/20260925_035112_847.log) | completed |
| `FossifyOrg_Gallery_940 Tested` | ✅ SUCCESS | 3 | [20260925_042817_611.log](../../Results-retest-merge/swipe/FossifyOrg_Gallery_940%20Tested/20260925_042817_611.log) | completed |
| `FossifyOrg_Launcher_66 Tested` | ✅ SUCCESS | 2 | [20260925_025627_005.log](../../Results-retest-merge/swipe/FossifyOrg_Launcher_66%20Tested/20260925_025627_005.log) | completed |
| `FossifyOrg_Messages_80 Tested` | ❌ FAILED | 2 | [20260925_035021_986.log](../../Results-retest-merge/swipe/FossifyOrg_Messages_80%20Tested/20260925_035021_986.log) | failed(loop) |
| `FossifyOrg_Notes_190 Tested` | ❌ FAILED | 1 | [20260922_222215_446.log](../../Results-retest-merge/swipe/FossifyOrg_Notes_190%20Tested/20260922_222215_446.log) | manual override (loop-abort) |
| `Kin69_EasyNotes_356 Tested` | ✅ SUCCESS | 2 | [20260925_034626_901.log](../../Results-retest-merge/swipe/Kin69_EasyNotes_356%20Tested/20260925_034626_901.log) | completed |
| `LawnchairLauncher_lawnchair_4642 Tested` | ✅ SUCCESS | 2 | [20260925_034849_201.log](../../Results-retest-merge/swipe/LawnchairLauncher_lawnchair_4642%20Tested/20260925_034849_201.log) | completed |
| `LawnchairLauncher_lawnchair_4708 Tested` | ❌ FAILED | 1 | [20260922_223439_952.log](../../Results-retest-merge/swipe/LawnchairLauncher_lawnchair_4708%20Tested/20260922_223439_952.log) | manual override (loop-abort) |
| `LawnchairLauncher_lawnchair_5496 Tested` | ✅ SUCCESS | 2 | [20260925_034735_164.log](../../Results-retest-merge/swipe/LawnchairLauncher_lawnchair_5496%20Tested/20260925_034735_164.log) | completed |
| `MetrolistGroup_Metrolist_3391 Tested` | ✅ SUCCESS | 1 | [20260922_224244_551.log](../../Results-retest-merge/swipe/MetrolistGroup_Metrolist_3391%20Tested/20260922_224244_551.log) | inferred (no FAILED line, token usage present) |
| `OuterTune_OuterTune_1044 Tested` | ❌ FAILED | 1 | [20260922_224901_419.log](../../Results-retest-merge/swipe/OuterTune_OuterTune_1044%20Tested/20260922_224901_419.log) | manual override (loop-abort) |
| `anilbeesetti_nextplayer_1127 Tested` | ✅ SUCCESS | 3 | [20260925_042815_305.log](../../Results-retest-merge/swipe/anilbeesetti_nextplayer_1127%20Tested/20260925_042815_305.log) | completed |
| `ankidroid_Anki-Android_14934 Tested F` | ❌ FAILED | 2 | [20260922_212100_901.log](../../Results-retest-merge/swipe/ankidroid_Anki-Android_14934%20Tested%20F/20260922_212100_901.log) | timeout (15 min limit) |
| `bartoostveen_ViTune_710 Tested` | ✅ SUCCESS | 3 | [20260925_042933_043.log](../../Results-retest-merge/swipe/bartoostveen_ViTune_710%20Tested/20260925_042933_043.log) | completed |
| `breezy-weather_breezy-weather_205 Tested` | ✅ SUCCESS | 2 | [20260925_035625_078.log](../../Results-retest-merge/swipe/breezy-weather_breezy-weather_205%20Tested/20260925_035625_078.log) | completed |
| `breezy-weather_breezy-weather_85 Tested` | ✅ SUCCESS | 2 | [20260925_034110_939.log](../../Results-retest-merge/swipe/breezy-weather_breezy-weather_85%20Tested/20260925_034110_939.log) | completed |
| `dessalines_thumb-key_371 Tested` | ✅ SUCCESS | 2 | [20260925_030122_710.log](../../Results-retest-merge/swipe/dessalines_thumb-key_371%20Tested/20260925_030122_710.log) | completed |
| `iamrasel_lunar-launcher_82 Tested` | ❌ FAILED | 4 | [20260925_055552_237.log](../../Results-retest-merge/swipe/iamrasel_lunar-launcher_82%20Tested/20260925_055552_237.log) | failed(timeout) |
| `libre-tube_LibreTube_8245 Tested` | ❌ FAILED | 2 | [20260925_035642_617.log](../../Results-retest-merge/swipe/libre-tube_LibreTube_8245%20Tested/20260925_035642_617.log) | agent could not load any content in the app to reach the playback step |
| `msasikanth_twine_1566 Tested` | ✅ SUCCESS | 2 | [20260925_035226_934.log](../../Results-retest-merge/swipe/msasikanth_twine_1566%20Tested/20260925_035226_934.log) | completed |
| `you-apps_ClockYou_85 Tested` | ❌ FAILED | 1 | [20260922_225143_578.log](../../Results-retest-merge/swipe/you-apps_ClockYou_85%20Tested/20260922_225143_578.log) | manual override (loop-abort) |
| `you-apps_ConnectYou_155 Tested` | ✅ SUCCESS | 1 | [20260922_225351_188.log](../../Results-retest-merge/swipe/you-apps_ConnectYou_155%20Tested/20260922_225351_188.log) | inferred (no FAILED line, token usage present) |
