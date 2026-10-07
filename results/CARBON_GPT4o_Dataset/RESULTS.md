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
run that was selected; the 188 source runs are kept alongside each case's
selected result, in that case's own `attempts/` subfolder.

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
| `FossifyOrg_Gallery_584` | double tap | Ran a different sequence from the one the report specifies, so the reported trigger was never performed. | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_584/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4786` | double tap | Could not produce the TalkBack 3-finger gesture the bug requires. | [carbon_gpt4o_log.txt](double_tap/LawnchairLauncher_lawnchair_4786/carbon_gpt4o_log.txt) |
| `openboard-team_openboard_758` | double tap | TalkBack was never enabled, so the screen-reader double-tap was never performed; the agent clicked `Navigate up`, saw it navigate correctly — the non-buggy behaviour — and called it a reproduction. Rejected on review. | [carbon_gpt4o_log.txt](double_tap/openboard-team_openboard_758/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_1247` | drag & drop | Could not produce the TalkBack `move` action the crash requires. | [carbon_gpt4o_log.txt](drag_and_drop/LawnchairLauncher_lawnchair_1247/carbon_gpt4o_log.txt) |
| `FossifyOrg_File-Manager_195` | long press | Claimed success without ever observing the icon refresh it set out to check. Rejected on review. | [carbon_gpt4o_log.txt](long_press/FossifyOrg_File-Manager_195/carbon_gpt4o_log.txt) |
| `anilbeesetti_nextplayer_1389` | quick tap | Never reached the resume step: repeated the same `quick_tap` on one player control with no state change until the loop guard stopped the run. | [carbon_gpt4o_log.txt](quick_tap/anilbeesetti_nextplayer_1389/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_18529` | quick tap | Never performed the mid-animation interaction this race needs. It tapped `+` on an empty deck list, hit an unrelated first-run ANR, and reported that as the bug. Rejected on review. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_18529/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_19641` | quick tap | Ran the full 60-minute limit without reaching the study screen: no card ever landed in the `test` deck (its counts stayed 0), so the answer-button step was unreachable. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_19641/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_20789` | quick tap | Blocked by a login wall before the AnkiWeb sync the notification depends on. | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_20789/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_5544` | scroll | Never got into the app: looped clicking `Search` on the device search screen while trying to find AnkiDroid. | [carbon_gpt4o_log.txt](scroll/ankidroid_Anki-Android_5544/carbon_gpt4o_log.txt) |
| `FossifyOrg_Calendar_153` | swipe | Never reached the calendar UI: alternated clicking the `Calendar` launcher icon and swiping until the loop guard stopped the run. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Calendar_153/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_80` | swipe | Loop guard stopped the run after three rounds of pressing `back` without the screen changing; the message thread was never reached. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Messages_80/carbon_gpt4o_log.txt) |
| `FossifyOrg_Notes_190` | swipe | Stuck on the theme dialog, bouncing between `Navigate up` and `OK`, and never reached the note list. | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Notes_190/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4708` | swipe | Could not open Recents: repeated bottom-edge swipe-ups never switched view, so the ghost-app check never ran. | [carbon_gpt4o_log.txt](swipe/LawnchairLauncher_lawnchair_4708/carbon_gpt4o_log.txt) |
| `OuterTune_OuterTune_1044` | swipe | Blocked by a new-folder dialog that never dismissed; repeated `OK` clicks left it on screen. | [carbon_gpt4o_log.txt](swipe/OuterTune_OuterTune_1044/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_14934` | swipe | Hit the 15-minute cap while looping through deck creation and sync dialogs; the card-study screen was never reached. | [carbon_gpt4o_log.txt](swipe/ankidroid_Anki-Android_14934/carbon_gpt4o_log.txt) |
| `iamrasel_lunar-launcher_82` | swipe | Spent the 30-minute limit on repeated swipe-up and `back` tries trying to get back to the launcher home screen, and was cut off before the repro step. | [carbon_gpt4o_log.txt](swipe/iamrasel_lunar-launcher_82/carbon_gpt4o_log.txt) |
| `libre-tube_LibreTube_8245` | swipe | No video content ever loaded, so the playback step the bug needs was never reached. | [carbon_gpt4o_log.txt](swipe/libre-tube_LibreTube_8245/carbon_gpt4o_log.txt) |
| `you-apps_ClockYou_85` | swipe | Lost in the quick-settings panel, alternating swipe up and swipe down, and never returned to the app. | [carbon_gpt4o_log.txt](swipe/you-apps_ClockYou_85/carbon_gpt4o_log.txt) |

Failure to reproduce does not establish that a bug is fixed.
Each reason above says what blocked that run, not whether the bug
still exists upstream.

Per-bug comparison between the two models:
[`CARBON_gemini-2.5-pro_vs_gpt-4o.md`](CARBON_gemini-2.5-pro_vs_gpt-4o.md).
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
- ``-tagged logs are read from their `FINAL status=` line:
  `completed` is a success; `failed(timeout)`, `failed(loop)`,
  `error(returncode=...)` and `apk_unavailable` are failures; a missing
  line means incomplete or truncated.
- `[run_dataset]`-tagged logs (the original pre-retest runs) carry no
  status line. Failure is marked by `[run_dataset] FAILED: exceeded 900s
  (15 min) time limit`. Absent that, a case is inferred successful only
  if it reaches a `token usage` summary **and** is not overturned by a
  `[CARBON RETEST -- MANUAL VERDICT] result: FAIL` block. **13 run logs
  across 12 cases carry such an override.** Of those 12 cases, 3
  (`ankidroid_Anki-Android_17667`, `FossifyOrg_Clock_85`,
  `gsantner_markor_2746`) later succeeded on a different attempt and so
  count as reproduced under the best-of-N rule above; the remaining **9
  are published as failures** in the table below.
- 5 untagged logs, all from 2026-09-20 and 2026-09-22, predate the tagging
  convention and died on repeated OpenAI API errors before any terminal
  marker; they are treated as incomplete.

### double_tap

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_1035` | ✅ SUCCESS | 1 | [20260920_175151_600.log](double_tap/FossifyOrg_Calendar_1035/attempts/20260920_175151_600.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Calendar_273` | ✅ SUCCESS | 1 | [20260920_181251_569.log](double_tap/FossifyOrg_Calendar_273/attempts/20260920_181251_569.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_363` | ✅ SUCCESS | 1 | [20260920_181254_572.log](double_tap/FossifyOrg_Gallery_363/attempts/20260920_181254_572.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_584` | ❌ FAILED | 3 | [20260925_024032_169.log](double_tap/FossifyOrg_Gallery_584/attempts/20260925_024032_169.log) | agent did not follow the reported repro steps, substituting its own scenario instead |
| `FossifyOrg_Gallery_678` | ✅ SUCCESS | 2 | [20260922_200151_551.log](double_tap/FossifyOrg_Gallery_678/attempts/20260922_200151_551.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_846` | ✅ SUCCESS | 1 | [20260920_181307_962.log](double_tap/FossifyOrg_Gallery_846/attempts/20260920_181307_962.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_847` | ✅ SUCCESS | 1 | [20260920_181309_561.log](double_tap/FossifyOrg_Gallery_847/attempts/20260920_181309_561.log) | inferred (no FAILED line, token usage present) |
| `LawnchairLauncher_lawnchair_2910` | ✅ SUCCESS | 1 | [20260920_181610_327.log](double_tap/LawnchairLauncher_lawnchair_2910/attempts/20260920_181610_327.log) | inferred (no FAILED line, token usage present) |
| `LawnchairLauncher_lawnchair_4125` | ✅ SUCCESS | 2 | [20260925_024149_700.log](double_tap/LawnchairLauncher_lawnchair_4125/attempts/20260925_024149_700.log) | completed |
| `LawnchairLauncher_lawnchair_4786` | ❌ FAILED | 2 | [20260925_024037_786.log](double_tap/LawnchairLauncher_lawnchair_4786/attempts/20260925_024037_786.log) | agent could not simulate the TalkBack 3-finger gesture required to trigger the bug |
| `Pool-Of-Tears_GreenStash_170` | ✅ SUCCESS | 2 | [20260925_023930_226.log](double_tap/Pool-Of-Tears_GreenStash_170/attempts/20260925_023930_226.log) | completed |
| `TeamNewPipe_NewPipe_10750` | ✅ SUCCESS | 3 | [20260925_023941_774.log](double_tap/TeamNewPipe_NewPipe_10750/attempts/20260925_023941_774.log) | completed |
| `TeamNewPipe_NewPipe_8338` | ✅ SUCCESS | 1 | [20260920_183520_067.log](double_tap/TeamNewPipe_NewPipe_8338/attempts/20260920_183520_067.log) | inferred (no FAILED line, token usage present) |
| `abdallahmehiz_mpvKt_184` | ✅ SUCCESS | 1 | [20260920_174647_056.log](double_tap/abdallahmehiz_mpvKt_184/attempts/20260920_174647_056.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_17393` | ✅ SUCCESS | 2 | [20260925_023937_155.log](double_tap/ankidroid_Anki-Android_17393/attempts/20260925_023937_155.log) | completed |
| `cromaguy_Rhythm_281` | ✅ SUCCESS | 1 | [20260920_174653_058.log](double_tap/cromaguy_Rhythm_281/attempts/20260920_174653_058.log) | inferred (no FAILED line, token usage present) |
| `fast4x_RiMusic_1152` | ✅ SUCCESS | 2 | [20260925_023924_627.log](double_tap/fast4x_RiMusic_1152/attempts/20260925_023924_627.log) | completed |
| `gsantner_markor_2746` | ✅ SUCCESS | 4 | [20260925_053933_979.log](double_tap/gsantner_markor_2746/attempts/20260925_053933_979.log) | completed |
| `openboard-team_openboard_613` | ✅ SUCCESS | 2 | [20260925_023942_136.log](double_tap/openboard-team_openboard_613/attempts/20260925_023942_136.log) | completed |
| `openboard-team_openboard_758` | ❌ FAILED | 1 | [20260920_182718_163.log](double_tap/openboard-team_openboard_758/attempts/20260920_182718_163.log) | manual override (false-positive correction) |
| `syt0r_Kanji-Dojo_291` | ✅ SUCCESS | 1 | [20260920_183205_040.log](double_tap/syt0r_Kanji-Dojo_291/attempts/20260920_183205_040.log) | inferred (no FAILED line, token usage present) |

### drag_and_drop

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Launcher_304` | ✅ SUCCESS | 2 | [20260925_023932_666.log](drag_and_drop/FossifyOrg_Launcher_304/attempts/20260925_023932_666.log) | completed |
| `FossifyOrg_Notes_59` | ✅ SUCCESS | 2 | [20260925_023938_347.log](drag_and_drop/FossifyOrg_Notes_59/attempts/20260925_023938_347.log) | completed |
| `LawnchairLauncher_lawnchair_1247` | ❌ FAILED | 2 | [20260925_030228_727.log](drag_and_drop/LawnchairLauncher_lawnchair_1247/attempts/20260925_030228_727.log) | agent could not simulate the TalkBack move action required to trigger the bug |
| `LawnchairLauncher_lawnchair_4320` | ✅ SUCCESS | 2 | [20260925_024715_703.log](drag_and_drop/LawnchairLauncher_lawnchair_4320/attempts/20260925_024715_703.log) | completed |
| `MetrolistGroup_Metrolist_3227` | ✅ SUCCESS | 4 | [20260925_073514_550.log](drag_and_drop/MetrolistGroup_Metrolist_3227/attempts/20260925_073514_550.log) | completed |
| `MetrolistGroup_Metrolist_3561` | ✅ SUCCESS | 1 | [20260920_185447_163.log](drag_and_drop/MetrolistGroup_Metrolist_3561/attempts/20260920_185447_163.log) | inferred (no FAILED line, token usage present) |
| `NeoApplications_Neo-Launcher_130` | ✅ SUCCESS | 4 | [20260925_073531_255.log](drag_and_drop/NeoApplications_Neo-Launcher_130/attempts/20260925_073531_255.log) | completed |
| `breezy-weather_breezy-weather_2159` | ✅ SUCCESS | 2 | [20260925_024931_925.log](drag_and_drop/breezy-weather_breezy-weather_2159/attempts/20260925_024931_925.log) | completed |
| `fcitx5-android_fcitx5-android_841` | ✅ SUCCESS | 4 | [20260925_073453_758.log](drag_and_drop/fcitx5-android_fcitx5-android_841/attempts/20260925_073453_758.log) | completed |

### long_press

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `Anthonyy232_Paperize_325` | ✅ SUCCESS | 2 | [20260925_024811_765.log](long_press/Anthonyy232_Paperize_325/attempts/20260925_024811_765.log) | completed |
| `Crustack_NotallyX_570` | ✅ SUCCESS | 4 | [20260925_073535_687.log](long_press/Crustack_NotallyX_570/attempts/20260925_073535_687.log) | completed |
| `FossifyOrg_File-Manager_195` | ❌ FAILED | 1 | [20260920_191238_869.log](long_press/FossifyOrg_File-Manager_195/attempts/20260920_191238_869.log) | agent claimed success without verifying the icon behavior it set out to check |
| `FossifyOrg_Launcher_198` | ✅ SUCCESS | 2 | [20260925_025316_313.log](long_press/FossifyOrg_Launcher_198/attempts/20260925_025316_313.log) | completed |
| `FossifyOrg_Messages_359` | ✅ SUCCESS | 1 | [20260920_191432_689.log](long_press/FossifyOrg_Messages_359/attempts/20260920_191432_689.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Messages_416` | ✅ SUCCESS | 2 | [20260925_025039_531.log](long_press/FossifyOrg_Messages_416/attempts/20260925_025039_531.log) | completed |
| `FossifyOrg_Messages_641` | ✅ SUCCESS | 7 | [20260925_111906_756.log](long_press/FossifyOrg_Messages_641/attempts/20260925_111906_756.log) | completed |
| `breezy-weather_breezy-weather_1639` | ✅ SUCCESS | 2 | [20260925_025659_590.log](long_press/breezy-weather_breezy-weather_1639/attempts/20260925_025659_590.log) | completed |
| `espresso3389_methings_34` | ✅ SUCCESS | 2 | [20260925_031355_254.log](long_press/espresso3389_methings_34/attempts/20260925_031355_254.log) | completed |

### orientation

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_1042` | ✅ SUCCESS | 1 | [20260920_192807_181.log](orientation/FossifyOrg_Calendar_1042/attempts/20260920_192807_181.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Camera_91` | ✅ SUCCESS | 1 | [20260920_193008_183.log](orientation/FossifyOrg_Camera_91/attempts/20260920_193008_183.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Clock_85` | ✅ SUCCESS | 5 | [20260925_111843_437.log](orientation/FossifyOrg_Clock_85/attempts/20260925_111843_437.log) | completed |
| `FossifyOrg_Contacts_197` | ✅ SUCCESS | 1 | [20260920_193309_421.log](orientation/FossifyOrg_Contacts_197/attempts/20260920_193309_421.log) | inferred (no FAILED line, token usage present) |
| `Waboodoo_HTTP-Shortcuts_262` | ✅ SUCCESS | 1 | [20260920_193316_693.log](orientation/Waboodoo_HTTP-Shortcuts_262/attempts/20260920_193316_693.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_16410` | ✅ SUCCESS | 1 | [20260920_192536_330.log](orientation/ankidroid_Anki-Android_16410/attempts/20260920_192536_330.log) | inferred (no FAILED line, token usage present) |

### pinch_zoom

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `FossifyOrg_Calendar_621` | ✅ SUCCESS | 2 | [20260925_025142_237.log](pinch_zoom/FossifyOrg_Calendar_621/attempts/20260925_025142_237.log) | completed |
| `FossifyOrg_Camera_23` | ✅ SUCCESS | 2 | [20260925_032220_040.log](pinch_zoom/FossifyOrg_Camera_23/attempts/20260925_032220_040.log) | completed |
| `FossifyOrg_Gallery_289` | ✅ SUCCESS | 1 | [20260920_194358_203.log](pinch_zoom/FossifyOrg_Gallery_289/attempts/20260920_194358_203.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_642` | ✅ SUCCESS | 1 | [20260920_195347_452.log](pinch_zoom/FossifyOrg_Gallery_642/attempts/20260920_195347_452.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Gallery_728` | ✅ SUCCESS | 1 | [20260922_203349_078.log](pinch_zoom/FossifyOrg_Gallery_728/attempts/20260922_203349_078.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Paint_125` | ✅ SUCCESS | 1 | [20260922_203703_465.log](pinch_zoom/FossifyOrg_Paint_125/attempts/20260922_203703_465.log) | inferred (no FAILED line, token usage present) |
| `FossifyOrg_Paint_25` | ✅ SUCCESS | 1 | [20260922_203843_036.log](pinch_zoom/FossifyOrg_Paint_25/attempts/20260922_203843_036.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_16135` | ✅ SUCCESS | 1 | [20260920_193602_254.log](pinch_zoom/ankidroid_Anki-Android_16135/attempts/20260920_193602_254.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_17667` | ✅ SUCCESS | 2 | [20260922_203347_838.log](pinch_zoom/ankidroid_Anki-Android_17667/attempts/20260922_203347_838.log) | inferred (no FAILED line, token usage present) |
| `saber-notes_saber_192` | ✅ SUCCESS | 1 | [20260922_204005_304.log](pinch_zoom/saber-notes_saber_192/attempts/20260922_204005_304.log) | inferred (no FAILED line, token usage present) |
| `streetcomplete_StreetComplete_6068` | ✅ SUCCESS | 1 | [20260922_204014_086.log](pinch_zoom/streetcomplete_StreetComplete_6068/attempts/20260922_204014_086.log) | inferred (no FAILED line, token usage present) |
| `you-apps_WallYou_216` | ✅ SUCCESS | 1 | [20260922_204059_713.log](pinch_zoom/you-apps_WallYou_216/attempts/20260922_204059_713.log) | inferred (no FAILED line, token usage present) |

### quick_tap

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `LawnchairLauncher_lawnchair_5540` | ✅ SUCCESS | 1 | [20260922_204821_633.log](quick_tap/LawnchairLauncher_lawnchair_5540/attempts/20260922_204821_633.log) | inferred (no FAILED line, token usage present) |
| `anilbeesetti_nextplayer_1389` | ❌ FAILED | 1 | [20260922_204211_248.log](quick_tap/anilbeesetti_nextplayer_1389/attempts/20260922_204211_248.log) | manual override (loop-abort) |
| `ankidroid_Anki-Android_18529` | ❌ FAILED | 1 | [20260922_204343_086.log](quick_tap/ankidroid_Anki-Android_18529/attempts/20260922_204343_086.log) | manual override (false-positive correction) |
| `ankidroid_Anki-Android_19641` | ❌ FAILED | 4 | [20260925_073508_329.log](quick_tap/ankidroid_Anki-Android_19641/attempts/20260925_073508_329.log) | failed(timeout) |
| `ankidroid_Anki-Android_20789` | ❌ FAILED | 3 | [20260925_044159_713.log](quick_tap/ankidroid_Anki-Android_20789/attempts/20260925_044159_713.log) | agent was blocked by a login/permission wall before reaching the sync step needed to trigger the bug |
| `ankidroid_Anki-Android_7138` | ✅ SUCCESS | 4 | [20260925_073519_517.log](quick_tap/ankidroid_Anki-Android_7138/attempts/20260925_073519_517.log) | completed |
| `yairm210_Unciv_13517` | ✅ SUCCESS | 2 | [20260925_025156_199.log](quick_tap/yairm210_Unciv_13517/attempts/20260925_025156_199.log) | completed |

### scroll

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `Anthonyy232_Paperize_426` | ✅ SUCCESS | 1 | [20260922_210327_443.log](scroll/Anthonyy232_Paperize_426/attempts/20260922_210327_443.log) | inferred (no FAILED line, token usage present) |
| `Fandroid745_Open-notes_15` | ✅ SUCCESS | 2 | [20260925_034709_490.log](scroll/Fandroid745_Open-notes_15/attempts/20260925_034709_490.log) | completed |
| `FossifyOrg_File-Manager_136` | ✅ SUCCESS | 2 | [20260925_034849_968.log](scroll/FossifyOrg_File-Manager_136/attempts/20260925_034849_968.log) | completed |
| `ankidroid_Anki-Android_5512` | ✅ SUCCESS | 1 | [20260922_210214_396.log](scroll/ankidroid_Anki-Android_5512/attempts/20260922_210214_396.log) | inferred (no FAILED line, token usage present) |
| `ankidroid_Anki-Android_5544` | ❌ FAILED | 1 | [20260922_210314_563.log](scroll/ankidroid_Anki-Android_5544/attempts/20260922_210314_563.log) | manual override (loop-abort) |
| `netmackan_ATimeTracker_124` | ✅ SUCCESS | 1 | [20260922_210902_839.log](scroll/netmackan_ATimeTracker_124/attempts/20260922_210902_839.log) | inferred (no FAILED line, token usage present) |

### swipe

| Case | Status | Attempts | Selected log | Detail |
|---|---|---|---|---|
| `A-EDev_Flow_27` | ✅ SUCCESS | 3 | [20260925_044241_668.log](swipe/A-EDev_Flow_27/attempts/20260925_044241_668.log) | completed |
| `A-EDev_Flow_284` | ✅ SUCCESS | 1 | [20260922_211655_125.log](swipe/A-EDev_Flow_284/attempts/20260922_211655_125.log) | inferred (no FAILED line, token usage present) |
| `CodeWorksCreativeHub_mLauncher_809` | ✅ SUCCESS | 2 | [20260925_032843_397.log](swipe/CodeWorksCreativeHub_mLauncher_809/attempts/20260925_032843_397.log) | completed |
| `Droid-ify_client_238` | ✅ SUCCESS | 2 | [20260925_034235_880.log](swipe/Droid-ify_client_238/attempts/20260925_034235_880.log) | completed |
| `Droid-ify_client_583` | ✅ SUCCESS | 2 | [20260925_025449_452.log](swipe/Droid-ify_client_583/attempts/20260925_025449_452.log) | completed |
| `FossifyOrg_Calendar_1103` | ✅ SUCCESS | 2 | [20260925_033155_885.log](swipe/FossifyOrg_Calendar_1103/attempts/20260925_033155_885.log) | completed |
| `FossifyOrg_Calendar_153` | ❌ FAILED | 1 | [20260922_215528_173.log](swipe/FossifyOrg_Calendar_153/attempts/20260922_215528_173.log) | manual override (loop-abort) |
| `FossifyOrg_Clock_156` | ✅ SUCCESS | 2 | [20260925_032456_487.log](swipe/FossifyOrg_Clock_156/attempts/20260925_032456_487.log) | completed |
| `FossifyOrg_Gallery_237` | ✅ SUCCESS | 2 | [20260925_035112_847.log](swipe/FossifyOrg_Gallery_237/attempts/20260925_035112_847.log) | completed |
| `FossifyOrg_Gallery_940` | ✅ SUCCESS | 3 | [20260925_042817_611.log](swipe/FossifyOrg_Gallery_940/attempts/20260925_042817_611.log) | completed |
| `FossifyOrg_Launcher_66` | ✅ SUCCESS | 2 | [20260925_025627_005.log](swipe/FossifyOrg_Launcher_66/attempts/20260925_025627_005.log) | completed |
| `FossifyOrg_Messages_80` | ❌ FAILED | 2 | [20260925_035021_986.log](swipe/FossifyOrg_Messages_80/attempts/20260925_035021_986.log) | failed(loop) |
| `FossifyOrg_Notes_190` | ❌ FAILED | 1 | [20260922_222215_446.log](swipe/FossifyOrg_Notes_190/attempts/20260922_222215_446.log) | manual override (loop-abort) |
| `Kin69_EasyNotes_356` | ✅ SUCCESS | 2 | [20260925_034626_901.log](swipe/Kin69_EasyNotes_356/attempts/20260925_034626_901.log) | completed |
| `LawnchairLauncher_lawnchair_4642` | ✅ SUCCESS | 2 | [20260925_034849_201.log](swipe/LawnchairLauncher_lawnchair_4642/attempts/20260925_034849_201.log) | completed |
| `LawnchairLauncher_lawnchair_4708` | ❌ FAILED | 1 | [20260922_223439_952.log](swipe/LawnchairLauncher_lawnchair_4708/attempts/20260922_223439_952.log) | manual override (loop-abort) |
| `LawnchairLauncher_lawnchair_5496` | ✅ SUCCESS | 2 | [20260925_034735_164.log](swipe/LawnchairLauncher_lawnchair_5496/attempts/20260925_034735_164.log) | completed |
| `MetrolistGroup_Metrolist_3391` | ✅ SUCCESS | 1 | [20260922_224244_551.log](swipe/MetrolistGroup_Metrolist_3391/attempts/20260922_224244_551.log) | inferred (no FAILED line, token usage present) |
| `OuterTune_OuterTune_1044` | ❌ FAILED | 1 | [20260922_224901_419.log](swipe/OuterTune_OuterTune_1044/attempts/20260922_224901_419.log) | manual override (loop-abort) |
| `anilbeesetti_nextplayer_1127` | ✅ SUCCESS | 3 | [20260925_042815_305.log](swipe/anilbeesetti_nextplayer_1127/attempts/20260925_042815_305.log) | completed |
| `ankidroid_Anki-Android_14934` | ❌ FAILED | 2 | [20260922_212100_901.log](swipe/ankidroid_Anki-Android_14934/attempts/20260922_212100_901.log) | timeout (15 min limit) |
| `bartoostveen_ViTune_710` | ✅ SUCCESS | 3 | [20260925_042933_043.log](swipe/bartoostveen_ViTune_710/attempts/20260925_042933_043.log) | completed |
| `breezy-weather_breezy-weather_205` | ✅ SUCCESS | 2 | [20260925_035625_078.log](swipe/breezy-weather_breezy-weather_205/attempts/20260925_035625_078.log) | completed |
| `breezy-weather_breezy-weather_85` | ✅ SUCCESS | 2 | [20260925_034110_939.log](swipe/breezy-weather_breezy-weather_85/attempts/20260925_034110_939.log) | completed |
| `dessalines_thumb-key_371` | ✅ SUCCESS | 2 | [20260925_030122_710.log](swipe/dessalines_thumb-key_371/attempts/20260925_030122_710.log) | completed |
| `iamrasel_lunar-launcher_82` | ❌ FAILED | 4 | [20260925_055552_237.log](swipe/iamrasel_lunar-launcher_82/attempts/20260925_055552_237.log) | failed(timeout) |
| `libre-tube_LibreTube_8245` | ❌ FAILED | 2 | [20260925_035642_617.log](swipe/libre-tube_LibreTube_8245/attempts/20260925_035642_617.log) | agent could not load any content in the app to reach the playback step |
| `msasikanth_twine_1566` | ✅ SUCCESS | 2 | [20260925_035226_934.log](swipe/msasikanth_twine_1566/attempts/20260925_035226_934.log) | completed |
| `you-apps_ClockYou_85` | ❌ FAILED | 1 | [20260922_225143_578.log](swipe/you-apps_ClockYou_85/attempts/20260922_225143_578.log) | manual override (loop-abort) |
| `you-apps_ConnectYou_155` | ✅ SUCCESS | 1 | [20260922_225351_188.log](swipe/you-apps_ConnectYou_155/attempts/20260922_225351_188.log) | inferred (no FAILED line, token usage present) |
