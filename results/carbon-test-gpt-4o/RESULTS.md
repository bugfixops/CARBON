# CARBON on GPT-4o — 100-Bug Gesture Benchmark

| | |
|---|---|
| Tool | CARBON |
| Model | `GPT-4o` |
| Cases tested | **100** |
| Reproduced | **81** (81.0%) |
| Not reproduced | **19** |

The same 100 bug reports as the `gemini-2.5-pro` campaign in the root
[`RESULTS.md`](../../RESULTS.md), run with GPT-4o as the backing model.
Each bug's log is `carbon_gpt4o_log.txt` in its folder. It ends with a
`VERDICT:` line (`SUCCESS` or `FAILED`) and a one-line `SUMMARY:`, and
the tables below match those lines.

The verdict is the agent's own final verdict, with manual corrections
where a run looped without progress (loop abort) or claimed a
reproduction that review overturned. A run stopped by its time limit or
by the loop guard counts as not reproduced. The table of the 19 failures
gives the reason for each.

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

Folder layout: [`README.md`](README.md).

## Appendix — all 100 cases

Each status is the `VERDICT:` line of that case's log.

### double_tap

| Case | Status | Log |
|---|---|---|
| `FossifyOrg_Calendar_1035` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Calendar_1035/carbon_gpt4o_log.txt) |
| `FossifyOrg_Calendar_273` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Calendar_273/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_363` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_363/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_584` | ❌ FAILED | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_584/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_678` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_678/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_846` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_846/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_847` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/FossifyOrg_Gallery_847/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_2910` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/LawnchairLauncher_lawnchair_2910/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4125` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/LawnchairLauncher_lawnchair_4125/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4786` | ❌ FAILED | [carbon_gpt4o_log.txt](double_tap/LawnchairLauncher_lawnchair_4786/carbon_gpt4o_log.txt) |
| `Pool-Of-Tears_GreenStash_170` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/Pool-Of-Tears_GreenStash_170/carbon_gpt4o_log.txt) |
| `TeamNewPipe_NewPipe_10750` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/TeamNewPipe_NewPipe_10750/carbon_gpt4o_log.txt) |
| `TeamNewPipe_NewPipe_8338` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/TeamNewPipe_NewPipe_8338/carbon_gpt4o_log.txt) |
| `abdallahmehiz_mpvKt_184` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/abdallahmehiz_mpvKt_184/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_17393` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/ankidroid_Anki-Android_17393/carbon_gpt4o_log.txt) |
| `cromaguy_Rhythm_281` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/cromaguy_Rhythm_281/carbon_gpt4o_log.txt) |
| `fast4x_RiMusic_1152` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/fast4x_RiMusic_1152/carbon_gpt4o_log.txt) |
| `gsantner_markor_2746` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/gsantner_markor_2746/carbon_gpt4o_log.txt) |
| `openboard-team_openboard_613` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/openboard-team_openboard_613/carbon_gpt4o_log.txt) |
| `openboard-team_openboard_758` | ❌ FAILED | [carbon_gpt4o_log.txt](double_tap/openboard-team_openboard_758/carbon_gpt4o_log.txt) |
| `syt0r_Kanji-Dojo_291` | ✅ SUCCESS | [carbon_gpt4o_log.txt](double_tap/syt0r_Kanji-Dojo_291/carbon_gpt4o_log.txt) |

### drag_and_drop

| Case | Status | Log |
|---|---|---|
| `FossifyOrg_Launcher_304` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/FossifyOrg_Launcher_304/carbon_gpt4o_log.txt) |
| `FossifyOrg_Notes_59` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/FossifyOrg_Notes_59/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_1247` | ❌ FAILED | [carbon_gpt4o_log.txt](drag_and_drop/LawnchairLauncher_lawnchair_1247/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4320` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/LawnchairLauncher_lawnchair_4320/carbon_gpt4o_log.txt) |
| `MetrolistGroup_Metrolist_3227` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/MetrolistGroup_Metrolist_3227/carbon_gpt4o_log.txt) |
| `MetrolistGroup_Metrolist_3561` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/MetrolistGroup_Metrolist_3561/carbon_gpt4o_log.txt) |
| `NeoApplications_Neo-Launcher_130` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/NeoApplications_Neo-Launcher_130/carbon_gpt4o_log.txt) |
| `breezy-weather_breezy-weather_2159` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/breezy-weather_breezy-weather_2159/carbon_gpt4o_log.txt) |
| `fcitx5-android_fcitx5-android_841` | ✅ SUCCESS | [carbon_gpt4o_log.txt](drag_and_drop/fcitx5-android_fcitx5-android_841/carbon_gpt4o_log.txt) |

### long_press

| Case | Status | Log |
|---|---|---|
| `Anthonyy232_Paperize_325` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/Anthonyy232_Paperize_325/carbon_gpt4o_log.txt) |
| `Crustack_NotallyX_570` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/Crustack_NotallyX_570/carbon_gpt4o_log.txt) |
| `FossifyOrg_File-Manager_195` | ❌ FAILED | [carbon_gpt4o_log.txt](long_press/FossifyOrg_File-Manager_195/carbon_gpt4o_log.txt) |
| `FossifyOrg_Launcher_198` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/FossifyOrg_Launcher_198/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_359` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/FossifyOrg_Messages_359/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_416` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/FossifyOrg_Messages_416/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_641` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/FossifyOrg_Messages_641/carbon_gpt4o_log.txt) |
| `breezy-weather_breezy-weather_1639` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/breezy-weather_breezy-weather_1639/carbon_gpt4o_log.txt) |
| `espresso3389_methings_34` | ✅ SUCCESS | [carbon_gpt4o_log.txt](long_press/espresso3389_methings_34/carbon_gpt4o_log.txt) |

### orientation

| Case | Status | Log |
|---|---|---|
| `FossifyOrg_Calendar_1042` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/FossifyOrg_Calendar_1042/carbon_gpt4o_log.txt) |
| `FossifyOrg_Camera_91` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/FossifyOrg_Camera_91/carbon_gpt4o_log.txt) |
| `FossifyOrg_Clock_85` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/FossifyOrg_Clock_85/carbon_gpt4o_log.txt) |
| `FossifyOrg_Contacts_197` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/FossifyOrg_Contacts_197/carbon_gpt4o_log.txt) |
| `Waboodoo_HTTP-Shortcuts_262` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/Waboodoo_HTTP-Shortcuts_262/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_16410` | ✅ SUCCESS | [carbon_gpt4o_log.txt](orientation/ankidroid_Anki-Android_16410/carbon_gpt4o_log.txt) |

### pinch_zoom

| Case | Status | Log |
|---|---|---|
| `FossifyOrg_Calendar_621` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Calendar_621/carbon_gpt4o_log.txt) |
| `FossifyOrg_Camera_23` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Camera_23/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_289` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Gallery_289/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_642` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Gallery_642/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_728` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Gallery_728/carbon_gpt4o_log.txt) |
| `FossifyOrg_Paint_125` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Paint_125/carbon_gpt4o_log.txt) |
| `FossifyOrg_Paint_25` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/FossifyOrg_Paint_25/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_16135` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/ankidroid_Anki-Android_16135/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_17667` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/ankidroid_Anki-Android_17667/carbon_gpt4o_log.txt) |
| `saber-notes_saber_192` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/saber-notes_saber_192/carbon_gpt4o_log.txt) |
| `streetcomplete_StreetComplete_6068` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/streetcomplete_StreetComplete_6068/carbon_gpt4o_log.txt) |
| `you-apps_WallYou_216` | ✅ SUCCESS | [carbon_gpt4o_log.txt](pinch_zoom/you-apps_WallYou_216/carbon_gpt4o_log.txt) |

### quick_tap

| Case | Status | Log |
|---|---|---|
| `LawnchairLauncher_lawnchair_5540` | ✅ SUCCESS | [carbon_gpt4o_log.txt](quick_tap/LawnchairLauncher_lawnchair_5540/carbon_gpt4o_log.txt) |
| `anilbeesetti_nextplayer_1389` | ❌ FAILED | [carbon_gpt4o_log.txt](quick_tap/anilbeesetti_nextplayer_1389/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_18529` | ❌ FAILED | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_18529/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_19641` | ❌ FAILED | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_19641/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_20789` | ❌ FAILED | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_20789/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_7138` | ✅ SUCCESS | [carbon_gpt4o_log.txt](quick_tap/ankidroid_Anki-Android_7138/carbon_gpt4o_log.txt) |
| `yairm210_Unciv_13517` | ✅ SUCCESS | [carbon_gpt4o_log.txt](quick_tap/yairm210_Unciv_13517/carbon_gpt4o_log.txt) |

### scroll

| Case | Status | Log |
|---|---|---|
| `Anthonyy232_Paperize_426` | ✅ SUCCESS | [carbon_gpt4o_log.txt](scroll/Anthonyy232_Paperize_426/carbon_gpt4o_log.txt) |
| `Fandroid745_Open-notes_15` | ✅ SUCCESS | [carbon_gpt4o_log.txt](scroll/Fandroid745_Open-notes_15/carbon_gpt4o_log.txt) |
| `FossifyOrg_File-Manager_136` | ✅ SUCCESS | [carbon_gpt4o_log.txt](scroll/FossifyOrg_File-Manager_136/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_5512` | ✅ SUCCESS | [carbon_gpt4o_log.txt](scroll/ankidroid_Anki-Android_5512/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_5544` | ❌ FAILED | [carbon_gpt4o_log.txt](scroll/ankidroid_Anki-Android_5544/carbon_gpt4o_log.txt) |
| `netmackan_ATimeTracker_124` | ✅ SUCCESS | [carbon_gpt4o_log.txt](scroll/netmackan_ATimeTracker_124/carbon_gpt4o_log.txt) |

### swipe

| Case | Status | Log |
|---|---|---|
| `A-EDev_Flow_27` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/A-EDev_Flow_27/carbon_gpt4o_log.txt) |
| `A-EDev_Flow_284` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/A-EDev_Flow_284/carbon_gpt4o_log.txt) |
| `CodeWorksCreativeHub_mLauncher_809` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/CodeWorksCreativeHub_mLauncher_809/carbon_gpt4o_log.txt) |
| `Droid-ify_client_238` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/Droid-ify_client_238/carbon_gpt4o_log.txt) |
| `Droid-ify_client_583` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/Droid-ify_client_583/carbon_gpt4o_log.txt) |
| `FossifyOrg_Calendar_1103` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Calendar_1103/carbon_gpt4o_log.txt) |
| `FossifyOrg_Calendar_153` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Calendar_153/carbon_gpt4o_log.txt) |
| `FossifyOrg_Clock_156` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Clock_156/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_237` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Gallery_237/carbon_gpt4o_log.txt) |
| `FossifyOrg_Gallery_940` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Gallery_940/carbon_gpt4o_log.txt) |
| `FossifyOrg_Launcher_66` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Launcher_66/carbon_gpt4o_log.txt) |
| `FossifyOrg_Messages_80` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Messages_80/carbon_gpt4o_log.txt) |
| `FossifyOrg_Notes_190` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/FossifyOrg_Notes_190/carbon_gpt4o_log.txt) |
| `Kin69_EasyNotes_356` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/Kin69_EasyNotes_356/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4642` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/LawnchairLauncher_lawnchair_4642/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_4708` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/LawnchairLauncher_lawnchair_4708/carbon_gpt4o_log.txt) |
| `LawnchairLauncher_lawnchair_5496` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/LawnchairLauncher_lawnchair_5496/carbon_gpt4o_log.txt) |
| `MetrolistGroup_Metrolist_3391` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/MetrolistGroup_Metrolist_3391/carbon_gpt4o_log.txt) |
| `OuterTune_OuterTune_1044` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/OuterTune_OuterTune_1044/carbon_gpt4o_log.txt) |
| `anilbeesetti_nextplayer_1127` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/anilbeesetti_nextplayer_1127/carbon_gpt4o_log.txt) |
| `ankidroid_Anki-Android_14934` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/ankidroid_Anki-Android_14934/carbon_gpt4o_log.txt) |
| `bartoostveen_ViTune_710` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/bartoostveen_ViTune_710/carbon_gpt4o_log.txt) |
| `breezy-weather_breezy-weather_205` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/breezy-weather_breezy-weather_205/carbon_gpt4o_log.txt) |
| `breezy-weather_breezy-weather_85` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/breezy-weather_breezy-weather_85/carbon_gpt4o_log.txt) |
| `dessalines_thumb-key_371` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/dessalines_thumb-key_371/carbon_gpt4o_log.txt) |
| `iamrasel_lunar-launcher_82` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/iamrasel_lunar-launcher_82/carbon_gpt4o_log.txt) |
| `libre-tube_LibreTube_8245` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/libre-tube_LibreTube_8245/carbon_gpt4o_log.txt) |
| `msasikanth_twine_1566` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/msasikanth_twine_1566/carbon_gpt4o_log.txt) |
| `you-apps_ClockYou_85` | ❌ FAILED | [carbon_gpt4o_log.txt](swipe/you-apps_ClockYou_85/carbon_gpt4o_log.txt) |
| `you-apps_ConnectYou_155` | ✅ SUCCESS | [carbon_gpt4o_log.txt](swipe/you-apps_ConnectYou_155/carbon_gpt4o_log.txt) |
