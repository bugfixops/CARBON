# CARBON on the 100-report gesture benchmark

One run per bug report with Gemini 2.5 Pro on Vertex AI, Android 14 on a Pixel 4
emulator. Each case links to its reproduction log.

A bug counts as reproduced when its run ended on CARBON's success claim, as the
log shows: the verifier confirmed the claim; or, after two rejected claims,
the run ended on a third, unconfirmed one; or, with no verifier output, the
run's `Execution time` line follows the claim. A rejected claim after which
the run went on, or a log cut off before the run's end line, counts as not reproduced.
Each bug below notes how its run ended.

**84 of 100 reproduced (84%).**

| Gesture | Reproduced | Not reproduced | Total |
|---|---|---|---|
| `quick_tap` | 4 | 3 | 7 |
| `double_tap` | 18 | 3 | 21 |
| `long_press` | 9 | 0 | 9 |
| `swipe` | 22 | 8 | 30 |
| `scroll` | 6 | 0 | 6 |
| `drag_and_drop` | 8 | 1 | 9 |
| `pinch_zoom` | 12 | 0 | 12 |
| `orientation` | 5 | 1 | 6 |
| **Total** | **84** | **16** | **100** |

## How the runs ended

| How the run ended | Bugs | Counted as |
|---|---:|---|
| Verifier confirmed the claim | 82 | reproduced |
| Ended on a third claim the verifier did not confirm | 2 | reproduced |
| CARBON reported fail | 9 | not reproduced |
| Claim rejected by the verifier, then the log ends mid-run | 1 | not reproduced |
| Claim rejected by the verifier, then the log ends while waiting out Gemini rate limits | 1 | not reproduced |
| No verdict, as the device went offline | 1 | not reproduced |
| No verdict, as the log ends while waiting out Gemini rate limits | 1 | not reproduced |
| No verdict, as the log ends mid-run | 3 | not reproduced |

## Reproduced (84)

### quick_tap (4)

- [anilbeesetti_nextplayer_1389](quick_tap/anilbeesetti_nextplayer_1389/carbon_log.txt): verifier confirmed the claim
- [ankidroid_Anki-Android_18529](quick_tap/ankidroid_Anki-Android_18529/carbon_log.txt): verifier confirmed the claim
- [ankidroid_Anki-Android_19641](quick_tap/ankidroid_Anki-Android_19641/carbon_log.txt): verifier confirmed the claim
- [yairm210_Unciv_13517](quick_tap/yairm210_Unciv_13517/carbon_log.txt): verifier confirmed the claim

### double_tap (18)

- [abdallahmehiz_mpvKt_184](double_tap/abdallahmehiz_mpvKt_184/carbon_log.txt): verifier confirmed the claim
- [ankidroid_Anki-Android_17393](double_tap/ankidroid_Anki-Android_17393/carbon_log.txt): verifier confirmed the claim
- [cromaguy_Rhythm_281](double_tap/cromaguy_Rhythm_281/carbon_log.txt): verifier confirmed the claim
- [fast4x_RiMusic_1152](double_tap/fast4x_RiMusic_1152/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Calendar_1035](double_tap/FossifyOrg_Calendar_1035/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Calendar_273](double_tap/FossifyOrg_Calendar_273/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_363](double_tap/FossifyOrg_Gallery_363/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_678](double_tap/FossifyOrg_Gallery_678/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_846](double_tap/FossifyOrg_Gallery_846/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_847](double_tap/FossifyOrg_Gallery_847/carbon_log.txt): verifier confirmed the claim
- [gsantner_markor_2746](double_tap/gsantner_markor_2746/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_2910](double_tap/LawnchairLauncher_lawnchair_2910/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_4125](double_tap/LawnchairLauncher_lawnchair_4125/carbon_log.txt): verifier confirmed the claim
- [openboard-team_openboard_613](double_tap/openboard-team_openboard_613/carbon_log.txt): ended on a third claim the verifier did not confirm
- [openboard-team_openboard_758](double_tap/openboard-team_openboard_758/carbon_log.txt): verifier confirmed the claim
- [Pool-Of-Tears_GreenStash_170](double_tap/Pool-Of-Tears_GreenStash_170/carbon_log.txt): verifier confirmed the claim
- [syt0r_Kanji-Dojo_291](double_tap/syt0r_Kanji-Dojo_291/carbon_log.txt): verifier confirmed the claim
- [TeamNewPipe_NewPipe_10750](double_tap/TeamNewPipe_NewPipe_10750/carbon_log.txt): verifier confirmed the claim

### long_press (9)

- [Anthonyy232_Paperize_325](long_press/Anthonyy232_Paperize_325/carbon_log.txt): verifier confirmed the claim
- [breezy-weather_breezy-weather_1639](long_press/breezy-weather_breezy-weather_1639/carbon_log.txt): verifier confirmed the claim
- [Crustack_NotallyX_570](long_press/Crustack_NotallyX_570/carbon_log.txt): verifier confirmed the claim
- [espresso3389_methings_34](long_press/espresso3389_methings_34/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_File-Manager_195](long_press/FossifyOrg_File-Manager_195/carbon_log.txt): ended on a third claim the verifier did not confirm
- [FossifyOrg_Launcher_198](long_press/FossifyOrg_Launcher_198/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Messages_359](long_press/FossifyOrg_Messages_359/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Messages_416](long_press/FossifyOrg_Messages_416/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Messages_641](long_press/FossifyOrg_Messages_641/carbon_log.txt): verifier confirmed the claim

### swipe (22)

- [A-EDev_Flow_27](swipe/A-EDev_Flow_27/carbon_log.txt): verifier confirmed the claim
- [bartoostveen_ViTune_710](swipe/bartoostveen_ViTune_710/carbon_log.txt): verifier confirmed the claim
- [breezy-weather_breezy-weather_205](swipe/breezy-weather_breezy-weather_205/carbon_log.txt): verifier confirmed the claim
- [CodeWorksCreativeHub_mLauncher_809](swipe/CodeWorksCreativeHub_mLauncher_809/carbon_log.txt): verifier confirmed the claim
- [dessalines_thumb-key_371](swipe/dessalines_thumb-key_371/carbon_log.txt): verifier confirmed the claim
- [Droid-ify_client_238](swipe/Droid-ify_client_238/carbon_log.txt): verifier confirmed the claim
- [Droid-ify_client_583](swipe/Droid-ify_client_583/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Calendar_153](swipe/FossifyOrg_Calendar_153/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Clock_156](swipe/FossifyOrg_Clock_156/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_237](swipe/FossifyOrg_Gallery_237/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_940](swipe/FossifyOrg_Gallery_940/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Launcher_66](swipe/FossifyOrg_Launcher_66/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Messages_80](swipe/FossifyOrg_Messages_80/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Notes_190](swipe/FossifyOrg_Notes_190/carbon_log.txt): verifier confirmed the claim
- [Kin69_EasyNotes_356](swipe/Kin69_EasyNotes_356/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_4642](swipe/LawnchairLauncher_lawnchair_4642/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_4708](swipe/LawnchairLauncher_lawnchair_4708/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_5496](swipe/LawnchairLauncher_lawnchair_5496/carbon_log.txt): verifier confirmed the claim
- [msasikanth_twine_1566](swipe/msasikanth_twine_1566/carbon_log.txt): verifier confirmed the claim
- [OuterTune_OuterTune_1044](swipe/OuterTune_OuterTune_1044/carbon_log.txt): verifier confirmed the claim
- [you-apps_ClockYou_85](swipe/you-apps_ClockYou_85/carbon_log.txt): verifier confirmed the claim
- [you-apps_ConnectYou_155](swipe/you-apps_ConnectYou_155/carbon_log.txt): verifier confirmed the claim

### scroll (6)

- [ankidroid_Anki-Android_5512](scroll/ankidroid_Anki-Android_5512/carbon_log.txt): verifier confirmed the claim
- [ankidroid_Anki-Android_5544](scroll/ankidroid_Anki-Android_5544/carbon_log.txt): verifier confirmed the claim
- [Anthonyy232_Paperize_426](scroll/Anthonyy232_Paperize_426/carbon_log.txt): verifier confirmed the claim
- [Fandroid745_Open-notes_15](scroll/Fandroid745_Open-notes_15/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_File-Manager_136](scroll/FossifyOrg_File-Manager_136/carbon_log.txt): verifier confirmed the claim
- [netmackan_ATimeTracker_124](scroll/netmackan_ATimeTracker_124/carbon_log.txt): verifier confirmed the claim

### drag_and_drop (8)

- [breezy-weather_breezy-weather_2159](drag_and_drop/breezy-weather_breezy-weather_2159/carbon_log.txt): verifier confirmed the claim
- [fcitx5-android_fcitx5-android_841](drag_and_drop/fcitx5-android_fcitx5-android_841/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Launcher_304](drag_and_drop/FossifyOrg_Launcher_304/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Notes_59](drag_and_drop/FossifyOrg_Notes_59/carbon_log.txt): verifier confirmed the claim
- [LawnchairLauncher_lawnchair_4320](drag_and_drop/LawnchairLauncher_lawnchair_4320/carbon_log.txt): verifier confirmed the claim
- [MetrolistGroup_Metrolist_3227](drag_and_drop/MetrolistGroup_Metrolist_3227/carbon_log.txt): verifier confirmed the claim
- [MetrolistGroup_Metrolist_3561](drag_and_drop/MetrolistGroup_Metrolist_3561/carbon_log.txt): verifier confirmed the claim
- [NeoApplications_Neo-Launcher_130](drag_and_drop/NeoApplications_Neo-Launcher_130/carbon_log.txt): verifier confirmed the claim

### pinch_zoom (12)

- [ankidroid_Anki-Android_16135](pinch_zoom/ankidroid_Anki-Android_16135/carbon_log.txt): verifier confirmed the claim
- [ankidroid_Anki-Android_17667](pinch_zoom/ankidroid_Anki-Android_17667/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Calendar_621](pinch_zoom/FossifyOrg_Calendar_621/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Camera_23](pinch_zoom/FossifyOrg_Camera_23/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_289](pinch_zoom/FossifyOrg_Gallery_289/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_642](pinch_zoom/FossifyOrg_Gallery_642/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Gallery_728](pinch_zoom/FossifyOrg_Gallery_728/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Paint_125](pinch_zoom/FossifyOrg_Paint_125/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Paint_25](pinch_zoom/FossifyOrg_Paint_25/carbon_log.txt): verifier confirmed the claim
- [saber-notes_saber_192](pinch_zoom/saber-notes_saber_192/carbon_log.txt): verifier confirmed the claim
- [streetcomplete_StreetComplete_6068](pinch_zoom/streetcomplete_StreetComplete_6068/carbon_log.txt): verifier confirmed the claim
- [you-apps_WallYou_216](pinch_zoom/you-apps_WallYou_216/carbon_log.txt): verifier confirmed the claim

### orientation (5)

- [ankidroid_Anki-Android_16410](orientation/ankidroid_Anki-Android_16410/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Calendar_1042](orientation/FossifyOrg_Calendar_1042/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Camera_91](orientation/FossifyOrg_Camera_91/carbon_log.txt): verifier confirmed the claim
- [FossifyOrg_Clock_85](orientation/FossifyOrg_Clock_85/carbon_log.txt): verifier confirmed the claim
- [Waboodoo_HTTP-Shortcuts_262](orientation/Waboodoo_HTTP-Shortcuts_262/carbon_log.txt): verifier confirmed the claim

## Not reproduced (16)

### quick_tap (3)

- [ankidroid_Anki-Android_20789](quick_tap/ankidroid_Anki-Android_20789/carbon_log.txt): CARBON reported fail
- [ankidroid_Anki-Android_7138](quick_tap/ankidroid_Anki-Android_7138/carbon_log.txt): CARBON reported fail
- [LawnchairLauncher_lawnchair_5540](quick_tap/LawnchairLauncher_lawnchair_5540/carbon_log.txt): no verdict, as the log ends while waiting out Gemini rate limits

### double_tap (3)

- [FossifyOrg_Gallery_584](double_tap/FossifyOrg_Gallery_584/carbon_log.txt): claim rejected by the verifier, then the log ends mid-run
- [LawnchairLauncher_lawnchair_4786](double_tap/LawnchairLauncher_lawnchair_4786/carbon_log.txt): CARBON reported fail
- [TeamNewPipe_NewPipe_8338](double_tap/TeamNewPipe_NewPipe_8338/carbon_log.txt): no verdict, as the log ends mid-run

### swipe (8)

- [A-EDev_Flow_284](swipe/A-EDev_Flow_284/carbon_log.txt): no verdict, as the device went offline
- [anilbeesetti_nextplayer_1127](swipe/anilbeesetti_nextplayer_1127/carbon_log.txt): CARBON reported fail
- [ankidroid_Anki-Android_14934](swipe/ankidroid_Anki-Android_14934/carbon_log.txt): CARBON reported fail
- [breezy-weather_breezy-weather_85](swipe/breezy-weather_breezy-weather_85/carbon_log.txt): no verdict, as the log ends mid-run
- [FossifyOrg_Calendar_1103](swipe/FossifyOrg_Calendar_1103/carbon_log.txt): CARBON reported fail
- [iamrasel_lunar-launcher_82](swipe/iamrasel_lunar-launcher_82/carbon_log.txt): claim rejected by the verifier, then the log ends while waiting out Gemini rate limits
- [libre-tube_LibreTube_8245](swipe/libre-tube_LibreTube_8245/carbon_log.txt): no verdict, as the log ends mid-run
- [MetrolistGroup_Metrolist_3391](swipe/MetrolistGroup_Metrolist_3391/carbon_log.txt): CARBON reported fail

### drag_and_drop (1)

- [LawnchairLauncher_lawnchair_1247](drag_and_drop/LawnchairLauncher_lawnchair_1247/carbon_log.txt): CARBON reported fail

### orientation (1)

- [FossifyOrg_Contacts_197](orientation/FossifyOrg_Contacts_197/carbon_log.txt): CARBON reported fail
