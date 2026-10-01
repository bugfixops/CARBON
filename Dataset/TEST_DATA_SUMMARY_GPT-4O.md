# Carbon-100 Test Results Summary

Source: `Results-retest-merge/` — 100 test cases across 8 gesture categories, 188 total log files.

For each case, when multiple log attempts existed, the run was resolved by:
1. Prefer a **SUCCESS** run (most recent one, if several succeeded).
2. Otherwise, prefer the **FAILED** run with the fullest/most complete log (largest file, most recent as tiebreak).
3. Otherwise, fall back to the most complete **INCOMPLETE** (truncated) log.

Status reflects the agent's own final verdict in the log transcript, not just
whether the harness run finished without a technical error.

## Overall Totals

| Status | Count | % of total |
|---|---|---|
| ✅ Success | 81 | 81.0% |
| ❌ Failed | 19 | 19.0% |
| **Total** | **100** | 100% |

## Breakdown by Category

| Category | Total | Success | Failed |
|---|---|---|---|
| double_tap | 21 | 18 | 3 |
| drag_and_drop | 9 | 8 | 1 |
| long_press | 9 | 8 | 1 |
| orientation | 6 | 6 | 0 |
| pinch_zoom | 12 | 12 | 0 |
| quick_tap | 7 | 3 | 4 |
| scroll | 6 | 5 | 1 |
| swipe | 30 | 21 | 9 |
| **Total** | **100** | **81** | **19** |

## Per-Case Detail

Each row shows the resolved status for the case and which log file was selected as the representative log (see rule above). The "Attempts" column shows how many log files existed for that case.

### double_tap

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| FossifyOrg_Calendar_1035 Tested | ✅ SUCCESS | 1 | `double_tap/FossifyOrg_Calendar_1035 Tested/20260920_175151_600.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Calendar_273 Tested | ✅ SUCCESS | 1 | `double_tap/FossifyOrg_Calendar_273 Tested/20260920_181251_569.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_363 Tested | ✅ SUCCESS | 1 | `double_tap/FossifyOrg_Gallery_363 Tested/20260920_181254_572.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_584 Tested F | ❌ FAILED | 3 | `double_tap/FossifyOrg_Gallery_584 Tested F/20260925_024032_169.log` | agent did not follow the reported repro steps, substituting its own scenario instead |
| FossifyOrg_Gallery_678 Tested | ✅ SUCCESS | 2 | `double_tap/FossifyOrg_Gallery_678 Tested/20260922_200151_551.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_846 Tested | ✅ SUCCESS | 1 | `double_tap/FossifyOrg_Gallery_846 Tested/20260920_181307_962.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_847 Tested | ✅ SUCCESS | 1 | `double_tap/FossifyOrg_Gallery_847 Tested/20260920_181309_561.log` | inferred (no FAILED line, token usage present) |
| LawnchairLauncher_lawnchair_2910 Tested | ✅ SUCCESS | 1 | `double_tap/LawnchairLauncher_lawnchair_2910 Tested/20260920_181610_327.log` | inferred (no FAILED line, token usage present) |
| LawnchairLauncher_lawnchair_4125 Tested | ✅ SUCCESS | 2 | `double_tap/LawnchairLauncher_lawnchair_4125 Tested/20260925_024149_700.log` | completed |
| LawnchairLauncher_lawnchair_4786 Tested F | ❌ FAILED | 2 | `double_tap/LawnchairLauncher_lawnchair_4786 Tested F/20260925_024037_786.log` | agent could not simulate the TalkBack 3-finger gesture required to trigger the bug |
| Pool-Of-Tears_GreenStash_170 Tested | ✅ SUCCESS | 2 | `double_tap/Pool-Of-Tears_GreenStash_170 Tested/20260925_023930_226.log` | completed |
| TeamNewPipe_NewPipe_10750 Tested | ✅ SUCCESS | 3 | `double_tap/TeamNewPipe_NewPipe_10750 Tested/20260925_023941_774.log` | completed |
| TeamNewPipe_NewPipe_8338 Tested | ✅ SUCCESS | 1 | `double_tap/TeamNewPipe_NewPipe_8338 Tested/20260920_183520_067.log` | inferred (no FAILED line, token usage present) |
| abdallahmehiz_mpvKt_184 Tested | ✅ SUCCESS | 1 | `double_tap/abdallahmehiz_mpvKt_184 Tested/20260920_174647_056.log` | inferred (no FAILED line, token usage present) |
| ankidroid_Anki-Android_17393 Tested | ✅ SUCCESS | 2 | `double_tap/ankidroid_Anki-Android_17393 Tested/20260925_023937_155.log` | completed |
| cromaguy_Rhythm_281 Tested | ✅ SUCCESS | 1 | `double_tap/cromaguy_Rhythm_281 Tested/20260920_174653_058.log` | inferred (no FAILED line, token usage present) |
| fast4x_RiMusic_1152 Tested | ✅ SUCCESS | 2 | `double_tap/fast4x_RiMusic_1152 Tested/20260925_023924_627.log` | completed |
| gsantner_markor_2746 Tested | ✅ SUCCESS | 4 | `double_tap/gsantner_markor_2746 Tested/20260925_053933_979.log` | completed |
| openboard-team_openboard_613 Tested | ✅ SUCCESS | 2 | `double_tap/openboard-team_openboard_613 Tested/20260925_023942_136.log` | completed |
| openboard-team_openboard_758 Tested F | ❌ FAILED | 1 | `double_tap/openboard-team_openboard_758 Tested F/20260920_182718_163.log` | manual override (false-positive correction) |
| syt0r_Kanji-Dojo_291 Tested | ✅ SUCCESS | 1 | `double_tap/syt0r_Kanji-Dojo_291 Tested/20260920_183205_040.log` | inferred (no FAILED line, token usage present) |

### drag_and_drop

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| FossifyOrg_Launcher_304 Tested | ✅ SUCCESS | 2 | `drag_and_drop/FossifyOrg_Launcher_304 Tested/20260925_023932_666.log` | completed |
| FossifyOrg_Notes_59 Tested | ✅ SUCCESS | 2 | `drag_and_drop/FossifyOrg_Notes_59 Tested/20260925_023938_347.log` | completed |
| LawnchairLauncher_lawnchair_1247 Tested F | ❌ FAILED | 2 | `drag_and_drop/LawnchairLauncher_lawnchair_1247 Tested F/20260925_030228_727.log` | agent could not simulate the TalkBack move action required to trigger the bug |
| LawnchairLauncher_lawnchair_4320 Tested | ✅ SUCCESS | 2 | `drag_and_drop/LawnchairLauncher_lawnchair_4320 Tested/20260925_024715_703.log` | completed |
| MetrolistGroup_Metrolist_3227 Tested | ✅ SUCCESS | 4 | `drag_and_drop/MetrolistGroup_Metrolist_3227 Tested/20260925_073514_550.log` | completed |
| MetrolistGroup_Metrolist_3561 Tested | ✅ SUCCESS | 1 | `drag_and_drop/MetrolistGroup_Metrolist_3561 Tested/20260920_185447_163.log` | inferred (no FAILED line, token usage present) |
| NeoApplications_Neo-Launcher_130 Tested | ✅ SUCCESS | 4 | `drag_and_drop/NeoApplications_Neo-Launcher_130 Tested/20260925_073531_255.log` | completed |
| breezy-weather_breezy-weather_2159 Tested | ✅ SUCCESS | 2 | `drag_and_drop/breezy-weather_breezy-weather_2159 Tested/20260925_024931_925.log` | completed |
| fcitx5-android_fcitx5-android_841 Tested | ✅ SUCCESS | 4 | `drag_and_drop/fcitx5-android_fcitx5-android_841 Tested/20260925_073453_758.log` | completed |

### long_press

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| Anthonyy232_Paperize_325 Tested | ✅ SUCCESS | 2 | `long_press/Anthonyy232_Paperize_325 Tested/20260925_024811_765.log` | completed |
| Crustack_NotallyX_570 Tested | ✅ SUCCESS | 4 | `long_press/Crustack_NotallyX_570 Tested/20260925_073535_687.log` | completed |
| FossifyOrg_File-Manager_195 Tested | ❌ FAILED | 1 | `long_press/FossifyOrg_File-Manager_195 Tested/20260920_191238_869.log` | agent claimed success without verifying the icon behavior it set out to check |
| FossifyOrg_Launcher_198 Tested | ✅ SUCCESS | 2 | `long_press/FossifyOrg_Launcher_198 Tested/20260925_025316_313.log` | completed |
| FossifyOrg_Messages_359 Tested | ✅ SUCCESS | 1 | `long_press/FossifyOrg_Messages_359 Tested/20260920_191432_689.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Messages_416 Tested | ✅ SUCCESS | 2 | `long_press/FossifyOrg_Messages_416 Tested/20260925_025039_531.log` | completed |
| FossifyOrg_Messages_641 Tested | ✅ SUCCESS | 7 | `long_press/FossifyOrg_Messages_641 Tested/20260925_111906_756.log` | completed |
| breezy-weather_breezy-weather_1639 Tested | ✅ SUCCESS | 2 | `long_press/breezy-weather_breezy-weather_1639 Tested/20260925_025659_590.log` | completed |
| espresso3389_methings_34 Tested | ✅ SUCCESS | 2 | `long_press/espresso3389_methings_34 Tested/20260925_031355_254.log` | completed |

### orientation

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| FossifyOrg_Calendar_1042 Tested | ✅ SUCCESS | 1 | `orientation/FossifyOrg_Calendar_1042 Tested/20260920_192807_181.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Camera_91 Tested | ✅ SUCCESS | 1 | `orientation/FossifyOrg_Camera_91 Tested/20260920_193008_183.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Clock_85 Tested F | ✅ SUCCESS | 5 | `orientation/FossifyOrg_Clock_85 Tested F/20260925_111843_437.log` | completed |
| FossifyOrg_Contacts_197 Tested | ✅ SUCCESS | 1 | `orientation/FossifyOrg_Contacts_197 Tested/20260920_193309_421.log` | inferred (no FAILED line, token usage present) |
| Waboodoo_HTTP-Shortcuts_262 Tested | ✅ SUCCESS | 1 | `orientation/Waboodoo_HTTP-Shortcuts_262 Tested/20260920_193316_693.log` | inferred (no FAILED line, token usage present) |
| ankidroid_Anki-Android_16410 Tested | ✅ SUCCESS | 1 | `orientation/ankidroid_Anki-Android_16410 Tested/20260920_192536_330.log` | inferred (no FAILED line, token usage present) |

### pinch_zoom

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| FossifyOrg_Calendar_621 Tested | ✅ SUCCESS | 2 | `pinch_zoom/FossifyOrg_Calendar_621 Tested/20260925_025142_237.log` | completed |
| FossifyOrg_Camera_23 Tested | ✅ SUCCESS | 2 | `pinch_zoom/FossifyOrg_Camera_23 Tested/20260925_032220_040.log` | completed |
| FossifyOrg_Gallery_289 Tested | ✅ SUCCESS | 1 | `pinch_zoom/FossifyOrg_Gallery_289 Tested/20260920_194358_203.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_642 Tested | ✅ SUCCESS | 1 | `pinch_zoom/FossifyOrg_Gallery_642 Tested/20260920_195347_452.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Gallery_728 Tested | ✅ SUCCESS | 1 | `pinch_zoom/FossifyOrg_Gallery_728 Tested/20260922_203349_078.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Paint_125 Tested | ✅ SUCCESS | 1 | `pinch_zoom/FossifyOrg_Paint_125 Tested/20260922_203703_465.log` | inferred (no FAILED line, token usage present) |
| FossifyOrg_Paint_25 Tested | ✅ SUCCESS | 1 | `pinch_zoom/FossifyOrg_Paint_25 Tested/20260922_203843_036.log` | inferred (no FAILED line, token usage present) |
| ankidroid_Anki-Android_16135 Tested | ✅ SUCCESS | 1 | `pinch_zoom/ankidroid_Anki-Android_16135 Tested/20260920_193602_254.log` | inferred (no FAILED line, token usage present) |
| ankidroid_Anki-Android_17667 Tested | ✅ SUCCESS | 2 | `pinch_zoom/ankidroid_Anki-Android_17667 Tested/20260922_203347_838.log` | inferred (no FAILED line, token usage present) |
| saber-notes_saber_192 Tested | ✅ SUCCESS | 1 | `pinch_zoom/saber-notes_saber_192 Tested/20260922_204005_304.log` | inferred (no FAILED line, token usage present) |
| streetcomplete_StreetComplete_6068 Tested | ✅ SUCCESS | 1 | `pinch_zoom/streetcomplete_StreetComplete_6068 Tested/20260922_204014_086.log` | inferred (no FAILED line, token usage present) |
| you-apps_WallYou_216 Tested | ✅ SUCCESS | 1 | `pinch_zoom/you-apps_WallYou_216 Tested/20260922_204059_713.log` | inferred (no FAILED line, token usage present) |

### quick_tap

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| LawnchairLauncher_lawnchair_5540 Tested | ✅ SUCCESS | 1 | `quick_tap/LawnchairLauncher_lawnchair_5540 Tested/20260922_204821_633.log` | inferred (no FAILED line, token usage present) |
| anilbeesetti_nextplayer_1389 Tested | ❌ FAILED | 1 | `quick_tap/anilbeesetti_nextplayer_1389 Tested/20260922_204211_248.log` | manual override (loop-abort) |
| ankidroid_Anki-Android_18529 Tested F | ❌ FAILED | 1 | `quick_tap/ankidroid_Anki-Android_18529 Tested F/20260922_204343_086.log` | manual override (false-positive correction) |
| ankidroid_Anki-Android_19641 Tested | ❌ FAILED | 4 | `quick_tap/ankidroid_Anki-Android_19641 Tested/20260925_073508_329.log` | failed(timeout) |
| ankidroid_Anki-Android_20789 Tested F | ❌ FAILED | 3 | `quick_tap/ankidroid_Anki-Android_20789 Tested F/20260925_044159_713.log` | agent was blocked by a login/permission wall before reaching the sync step needed to trigger the bug |
| ankidroid_Anki-Android_7138 Tested | ✅ SUCCESS | 4 | `quick_tap/ankidroid_Anki-Android_7138 Tested/20260925_073519_517.log` | completed |
| yairm210_Unciv_13517 Tested | ✅ SUCCESS | 2 | `quick_tap/yairm210_Unciv_13517 Tested/20260925_025156_199.log` | completed |

### scroll

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| Anthonyy232_Paperize_426 Tested | ✅ SUCCESS | 1 | `scroll/Anthonyy232_Paperize_426 Tested/20260922_210327_443.log` | inferred (no FAILED line, token usage present) |
| Fandroid745_Open-notes_15 Tested | ✅ SUCCESS | 2 | `scroll/Fandroid745_Open-notes_15 Tested/20260925_034709_490.log` | completed |
| FossifyOrg_File-Manager_136 Tested | ✅ SUCCESS | 2 | `scroll/FossifyOrg_File-Manager_136 Tested/20260925_034849_968.log` | completed |
| ankidroid_Anki-Android_5512 Tested | ✅ SUCCESS | 1 | `scroll/ankidroid_Anki-Android_5512 Tested/20260922_210214_396.log` | inferred (no FAILED line, token usage present) |
| ankidroid_Anki-Android_5544 Tested | ❌ FAILED | 1 | `scroll/ankidroid_Anki-Android_5544 Tested/20260922_210314_563.log` | manual override (loop-abort) |
| netmackan_ATimeTracker_124 Tested | ✅ SUCCESS | 1 | `scroll/netmackan_ATimeTracker_124 Tested/20260922_210902_839.log` | inferred (no FAILED line, token usage present) |

### swipe

| Case | Status | Attempts | Selected Log | Detail |
|---|---|---|---|---|
| A-EDev_Flow_27 Tested | ✅ SUCCESS | 3 | `swipe/A-EDev_Flow_27 Tested/20260925_044241_668.log` | completed |
| A-EDev_Flow_284 Tested | ✅ SUCCESS | 1 | `swipe/A-EDev_Flow_284 Tested/20260922_211655_125.log` | inferred (no FAILED line, token usage present) |
| CodeWorksCreativeHub_mLauncher_809 Tested | ✅ SUCCESS | 2 | `swipe/CodeWorksCreativeHub_mLauncher_809 Tested/20260925_032843_397.log` | completed |
| Droid-ify_client_238 Tested | ✅ SUCCESS | 2 | `swipe/Droid-ify_client_238 Tested/20260925_034235_880.log` | completed |
| Droid-ify_client_583 Tested | ✅ SUCCESS | 2 | `swipe/Droid-ify_client_583 Tested/20260925_025449_452.log` | completed |
| FossifyOrg_Calendar_1103 Tested | ✅ SUCCESS | 2 | `swipe/FossifyOrg_Calendar_1103 Tested/20260925_033155_885.log` | completed |
| FossifyOrg_Calendar_153 Tested | ❌ FAILED | 1 | `swipe/FossifyOrg_Calendar_153 Tested/20260922_215528_173.log` | manual override (loop-abort) |
| FossifyOrg_Clock_156 Tested F | ✅ SUCCESS | 2 | `swipe/FossifyOrg_Clock_156 Tested F/20260925_032456_487.log` | completed |
| FossifyOrg_Gallery_237 Tested | ✅ SUCCESS | 2 | `swipe/FossifyOrg_Gallery_237 Tested/20260925_035112_847.log` | completed |
| FossifyOrg_Gallery_940 Tested | ✅ SUCCESS | 3 | `swipe/FossifyOrg_Gallery_940 Tested/20260925_042817_611.log` | completed |
| FossifyOrg_Launcher_66 Tested | ✅ SUCCESS | 2 | `swipe/FossifyOrg_Launcher_66 Tested/20260925_025627_005.log` | completed |
| FossifyOrg_Messages_80 Tested | ❌ FAILED | 2 | `swipe/FossifyOrg_Messages_80 Tested/20260925_035021_986.log` | failed(loop) |
| FossifyOrg_Notes_190 Tested | ❌ FAILED | 1 | `swipe/FossifyOrg_Notes_190 Tested/20260922_222215_446.log` | manual override (loop-abort) |
| Kin69_EasyNotes_356 Tested | ✅ SUCCESS | 2 | `swipe/Kin69_EasyNotes_356 Tested/20260925_034626_901.log` | completed |
| LawnchairLauncher_lawnchair_4642 Tested | ✅ SUCCESS | 2 | `swipe/LawnchairLauncher_lawnchair_4642 Tested/20260925_034849_201.log` | completed |
| LawnchairLauncher_lawnchair_4708 Tested | ❌ FAILED | 1 | `swipe/LawnchairLauncher_lawnchair_4708 Tested/20260922_223439_952.log` | manual override (loop-abort) |
| LawnchairLauncher_lawnchair_5496 Tested | ✅ SUCCESS | 2 | `swipe/LawnchairLauncher_lawnchair_5496 Tested/20260925_034735_164.log` | completed |
| MetrolistGroup_Metrolist_3391 Tested | ✅ SUCCESS | 1 | `swipe/MetrolistGroup_Metrolist_3391 Tested/20260922_224244_551.log` | inferred (no FAILED line, token usage present) |
| OuterTune_OuterTune_1044 Tested | ❌ FAILED | 1 | `swipe/OuterTune_OuterTune_1044 Tested/20260922_224901_419.log` | manual override (loop-abort) |
| anilbeesetti_nextplayer_1127 Tested | ✅ SUCCESS | 3 | `swipe/anilbeesetti_nextplayer_1127 Tested/20260925_042815_305.log` | completed |
| ankidroid_Anki-Android_14934 Tested F | ❌ FAILED | 2 | `swipe/ankidroid_Anki-Android_14934 Tested F/20260922_212100_901.log` | timeout (15 min limit) |
| bartoostveen_ViTune_710 Tested | ✅ SUCCESS | 3 | `swipe/bartoostveen_ViTune_710 Tested/20260925_042933_043.log` | completed |
| breezy-weather_breezy-weather_205 Tested | ✅ SUCCESS | 2 | `swipe/breezy-weather_breezy-weather_205 Tested/20260925_035625_078.log` | completed |
| breezy-weather_breezy-weather_85 Tested | ✅ SUCCESS | 2 | `swipe/breezy-weather_breezy-weather_85 Tested/20260925_034110_939.log` | completed |
| dessalines_thumb-key_371 Tested | ✅ SUCCESS | 2 | `swipe/dessalines_thumb-key_371 Tested/20260925_030122_710.log` | completed |
| iamrasel_lunar-launcher_82 Tested | ❌ FAILED | 4 | `swipe/iamrasel_lunar-launcher_82 Tested/20260925_055552_237.log` | failed(timeout) |
| libre-tube_LibreTube_8245 Tested | ❌ FAILED | 2 | `swipe/libre-tube_LibreTube_8245 Tested/20260925_035642_617.log` | agent could not load any content in the app to reach the playback step |
| msasikanth_twine_1566 Tested | ✅ SUCCESS | 2 | `swipe/msasikanth_twine_1566 Tested/20260925_035226_934.log` | completed |
| you-apps_ClockYou_85 Tested | ❌ FAILED | 1 | `swipe/you-apps_ClockYou_85 Tested/20260922_225143_578.log` | manual override (loop-abort) |
| you-apps_ConnectYou_155 Tested | ✅ SUCCESS | 1 | `swipe/you-apps_ConnectYou_155 Tested/20260922_225351_188.log` | inferred (no FAILED line, token usage present) |

## Notes

- Classification is derived purely from log content, not folder-name suffixes.
- `[run_retest]`-tagged logs are classified from their `FINAL status=` line (`completed` = success; `failed(timeout)`, `failed(loop)`, `error(returncode=...)`, `apk_unavailable` = failed; missing entirely = incomplete/truncated).
- `[run_dataset]`-tagged logs (the original, pre-retest runs) have no explicit status line. Failure is marked by a `[run_dataset] FAILED: exceeded 900s (15 min) time limit` line. Absent that, a case is inferred successful only if it reaches a `token usage` summary **and** is not overturned by a `[CARBON RETEST -- MANUAL VERDICT] result: FAIL` block (13 cases had an initial inferred-success verdict manually overturned on review).
- Untagged logs (5 total, all dated 2026-09-20/22) are pre-tagging-convention runs that crashed on repeated OpenAI API errors before reaching any terminal marker; treated as incomplete.
