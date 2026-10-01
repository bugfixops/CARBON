# CARBON over the full ReBL Dataset — Retest Campaign Results

| | |
|---|---|
| Dataset | the ReBL benchmark — **95 bug reports** (72 crash + 23 non-crash) |
| Tool | CARBON |
| Model | `gemini-2.5-pro` |
| Dates | 2026-09-26 to 2026-09-28 |
| Cases tested | **95** |
| Reproduced | **90 (94.7%)** |
| Not reproduced | **5** |

> **A different dataset from the 100-bug gesture benchmark.** These numbers are not comparable to the root [`RESULTS.md`](../../RESULTS.md) tables, which measure a separate 100-bug gesture-diverse benchmark. Nothing here counts toward those, and nothing there counts toward these.

## Summary

After the initial wave (**70/95**, 73.7%), all 25 failures were individually retested with targeted fixes (custom APKs, pre-setup scripts, improved agent hints, harness actions like `rapid_click` and `tap_then_swipe`, API level adjustments).

**Final tally: 90/95 (94.7%)** — 20 conversions.

The tally reconciles against the committed per-case evidence in this folder: 95 executed cases minus the 5 remaining `NOT_REPRODUCIBLE.md` files = 90 reproduced. One of those 90 — `hidroh_materialistic_1067` — is counted as reproduced **as an ANR**, not as the originally reported crash; see the footnote.

| Group | Tested | Reproduced | Not reproduced |
|---|---:|---:|---:|
| crash | 72 | 69 | 3 |
| non_crash | 23 | 21 | 2 |
| **Total** | **95** | **90** | **5** |

**90/95 is not a single-shot rate.** It is the outcome after one targeted retest pass over the 25 initial failures.

## Conversions (20)

| Case | Fix Applied |
|------|-------------|
| vestrel00_android-dagger-butterknife-mvp_46 | Corrected agent hint |
| citiususc_calendula_134 | Loop-guard tuning (max_repeat) |
| moezbhatti_qksms_1155 | Emulator-compatible repro path |
| andOTP_andOTP_567 | Bypassed setup blocker via pre_setup |
| zwieback_FamilyFinance_1 | Verified buggy code in APK via apktool |
| netmackan_ATimeTracker_10 | Emulator-compatible repro path |
| kiwix_kiwix-android_990 | F-Droid APK (correct build) |
| ankidroid_Anki-Android_4586 | API level 24 (matching report) |
| getodk_collect_2525 | Custom targetSdk24 APK build |
| brodeurlv_fastnfitness_142 | Loop-guard tuning |
| getodk_collect_1796 | Race-condition timing fix |
| y20k_transistor_149 | rapid_click harness action (30 taps) |
| commons-app_apps-android-commons_2123 | Onboarding swipe bypass via pre_setup |
| gsantner_markor_1698 | Corrected hint (API 26, let dialog reappear) |
| PhenoApps_Field-Book_145 | Database reset via Settings |
| ankidroid_Anki-Android_5753 | Non-crash HTML-strip verification |
| vijai1996_screenrecorder_25 | F-Droid 1.8.1 APK |
| mikepenz_FastAdapter_113 | Multiselect delete repro |
| ankidroid_Anki-Android_5638 | Wave-2 retest — FATAL EXCEPTION on backslash input |
| hidroh_materialistic_1067 | Wave-2 retest — timing/race repro; reproduced **as an ANR**, not the reported crash [^anr] |

[^anr]: **`hidroh_materialistic_1067` is counted as reproduced as an ANR, not as the reported crash.** The wave-2 retest triggered a genuine "Materialistic isn't responding" ANR dialog (Wait / Close app, confirmed in the UI dump) after save-then-swipe during loading, so the timing race is real and was provoked by the reported interaction. However, logcat contains **no FATAL EXCEPTION** for that run: the manifestation was a UI-thread freeze, not the reported crash, and the originally reported crash signature remains unconfirmed. Full evidence: [`crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md`](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md).

## Remaining 5 (not reproduced)

**Not reproduced under the tested conditions; causes remain partly unresolved.** Failure to reproduce does not establish that a bug is fixed. See each case folder's `NOT_REPRODUCIBLE.md` for the full evidence and caveats.

| Case | Status |
|------|--------|
| [MarcusWolschon_osmeditor4android_637](crash/MarcusWolschon_osmeditor4android_637/NOT_REPRODUCIBLE.md) | Not reproduced — the agent's own `success` verdict is **rejected**. In the wave-2 retest (90-minute timeout) the app ended up on the launcher after "Download current view", but logcat shows no FATAL EXCEPTION, no process-death marker, and the exception monitor (which caught real crashes in sibling runs) reported nothing. APK version 0.9.10.0.1324 matches the report. |
| [ankidroid_Anki-Android_6432](crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md) | Setup failure — two retests (45-minute and 1-hour timeouts) both timed out during the ~15-step custom note-type / clone / add-cards / multi-select setup without reaching the crash trigger. Harness and agent-capability limitation, not confirmation of a fix. |
| [getodk_collect_360](crash/getodk_collect_360/NOT_REPRODUCIBLE.md) | Skipped — reproduction requires Google OAuth sign-in, which the emulator cannot complete (no Play Services with valid credentials; adb cannot drive the account auth flow). No retest attempted, per the 2026-09-26 directive to skip Google-login APKs. Environment limitation, not a fix. |
| [beemdevelopment_Aegis_287](non_crash/beemdevelopment_Aegis_287/NOT_REPRODUCIBLE.md) | No-repro, confirmed by two independent runs (v6 and wave-2): with device locale fr-FR and the vault pre-created, the agent switched the language to English, force-stopped and relaunched, and the UI — including the settings screen — stayed English. Language persists correctly through restart. |
| [moezbhatti_qksms_1124](non_crash/moezbhatti_qksms_1124/NOT_REPRODUCIBLE.md) | Not reproduced on API 30 with app v3.1.3: the notification channel was set to "Silent" and persisted. Verified in v3.1.3 source that `NotificationPrefsActivity.onCreate` hides the in-app Sound preference on Android 8+ (`ringtone.setVisible(!hasOreo)`), routing sound config to the OS channel; the bug was reported on Android 6.0.1 where that in-app preference existed. A literal reproduction would require API ≤ 25. |

## Why the failures failed, grouped

| Cause | Count | Cases |
|---|---:|---|
| Environment cannot satisfy a prerequisite (third-party account / OS API level) | 2 | `getodk_collect_360`, `moezbhatti_qksms_1124` |
| Harness/agent limitation — multi-step setup not completed in the time limit | 1 | `ankidroid_Anki-Android_6432` |
| Agent success claim rejected — no corroborating crash signal | 1 | `MarcusWolschon_osmeditor4android_637` |
| Genuine no-repro on a report-matching build | 1 | `beemdevelopment_Aegis_287` |
| **Total** | **5** | |

## Per-case results (95 rows)

`Log verdict` is the verdict in that case's own `carbon_log.txt`; `Outcome` is what the case counts as, determined by the presence of a `NOT_REPRODUCIBLE.md` file. Where the two differ the agent's claim was rejected and the reason is given.

| # | Group | Case | Log verdict | Outcome | Note | Evidence |
|---:|---|---|:--:|:--:|---|---|
| 1 | crash | `ASU-CodeDevils_FlashCards_13` | `success` | ✅ reproduced |  | [log](crash/ASU-CodeDevils_FlashCards_13/carbon_log.txt) |
| 2 | crash | `AntennaPod_AntennaPod_3245` | `success` | ✅ reproduced |  | [log](crash/AntennaPod_AntennaPod_3245/carbon_log.txt) |
| 3 | crash | `CellularPrivacy_Android-IMSI-Catcher-Detector_816` | `success` | ✅ reproduced |  | [log](crash/CellularPrivacy_Android-IMSI-Catcher-Detector_816/carbon_log.txt) |
| 4 | crash | `MarcusWolschon_osmeditor4android_637` | `success` | ❌ not reproduced | Agent claimed success; no crash signature in logcat, claim rejected | [log](crash/MarcusWolschon_osmeditor4android_637/carbon_log.txt) · [NOT_REPRODUCIBLE](crash/MarcusWolschon_osmeditor4android_637/NOT_REPRODUCIBLE.md) |
| 5 | crash | `PhenoApps_Field-Book_145` | `success` | ✅ reproduced |  | [log](crash/PhenoApps_Field-Book_145/carbon_log.txt) |
| 6 | crash | `PhenoApps_Field-Book_146` | `success` | ✅ reproduced |  | [log](crash/PhenoApps_Field-Book_146/carbon_log.txt) |
| 7 | crash | `SecUSo_privacy-friendly-weather_61` | `success` | ✅ reproduced |  | [log](crash/SecUSo_privacy-friendly-weather_61/carbon_log.txt) |
| 8 | crash | `alexstojda_soen390_36` | `success` | ✅ reproduced |  | [log](crash/alexstojda_soen390_36/carbon_log.txt) |
| 9 | crash | `alexstyl_Memento-Calendar_169` | `success` | ✅ reproduced |  | [log](crash/alexstyl_Memento-Calendar_169/carbon_log.txt) |
| 10 | crash | `andOTP_andOTP_135` | `success` | ✅ reproduced |  | [log](crash/andOTP_andOTP_135/carbon_log.txt) |
| 11 | crash | `andOTP_andOTP_500` | `success` | ✅ reproduced |  | [log](crash/andOTP_andOTP_500/carbon_log.txt) |
| 12 | crash | `andOTP_andOTP_569` | `success` | ✅ reproduced |  | [log](crash/andOTP_andOTP_569/carbon_log.txt) |
| 13 | crash | `ankidroid_Anki-Android_4586` | `success` | ✅ reproduced |  | [log](crash/ankidroid_Anki-Android_4586/carbon_log.txt) |
| 14 | crash | `ankidroid_Anki-Android_5638` | `success` | ✅ reproduced |  | [log](crash/ankidroid_Anki-Android_5638/carbon_log.txt) |
| 15 | crash | `ankidroid_Anki-Android_6432` | *none (timed out)* | ❌ not reproduced | Two retests timed out during the ~15-step setup, before the trigger | [log](crash/ankidroid_Anki-Android_6432/carbon_log.txt) · [NOT_REPRODUCIBLE](crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md) · [earlier run](crash/ankidroid_Anki-Android_6432/logs/20260926_220929_344.log) |
| 16 | crash | `banderlabs_notepad_23` | `success` | ✅ reproduced |  | [log](crash/banderlabs_notepad_23/carbon_log.txt) |
| 17 | crash | `beemdevelopment_Aegis_500` | `success` | ✅ reproduced |  | [log](crash/beemdevelopment_Aegis_500/carbon_log.txt) |
| 18 | crash | `brodeurlv_fastnfitness_142` | `success` | ✅ reproduced |  | [log](crash/brodeurlv_fastnfitness_142/carbon_log.txt) |
| 19 | crash | `citiususc_calendula_134` | `success` | ✅ reproduced |  | [log](crash/citiususc_calendula_134/carbon_log.txt) |
| 20 | crash | `cohenadair_anglers-log_9` | `success` | ✅ reproduced |  | [log](crash/cohenadair_anglers-log_9/carbon_log.txt) |
| 21 | crash | `commons-app_apps-android-commons_2123` | `success` | ✅ reproduced |  | [log](crash/commons-app_apps-android-commons_2123/carbon_log.txt) |
| 22 | crash | `dozingcat_AsciiCam_17` | `success` | ✅ reproduced |  | [log](crash/dozingcat_AsciiCam_17/carbon_log.txt) |
| 23 | crash | `fdroid_fdroidclient_1821` | `success` | ✅ reproduced |  | [log](crash/fdroid_fdroidclient_1821/carbon_log.txt) |
| 24 | crash | `gauravjot_android-noad-music-player_1` | `success` | ✅ reproduced |  | [log](crash/gauravjot_android-noad-music-player_1/carbon_log.txt) |
| 25 | crash | `getodk_collect_1402` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_1402/carbon_log.txt) |
| 26 | crash | `getodk_collect_1796` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_1796/carbon_log.txt) |
| 27 | crash | `getodk_collect_2075` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_2075/carbon_log.txt) |
| 28 | crash | `getodk_collect_2086` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_2086/carbon_log.txt) |
| 29 | crash | `getodk_collect_2191` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_2191/carbon_log.txt) |
| 30 | crash | `getodk_collect_2525` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_2525/carbon_log.txt) |
| 31 | crash | `getodk_collect_3222` | `success` | ✅ reproduced |  | [log](crash/getodk_collect_3222/carbon_log.txt) |
| 32 | crash | `getodk_collect_360` | `fail` | ❌ not reproduced | Google OAuth sign-in not completable in the emulator | [log](crash/getodk_collect_360/carbon_log.txt) · [NOT_REPRODUCIBLE](crash/getodk_collect_360/NOT_REPRODUCIBLE.md) |
| 33 | crash | `gsantner_markor_1698` | `success` | ✅ reproduced |  | [log](crash/gsantner_markor_1698/carbon_log.txt) |
| 34 | crash | `gsantner_markor_194` | `success` | ✅ reproduced |  | [log](crash/gsantner_markor_194/carbon_log.txt) |
| 35 | crash | `helloworld1_AnyMemo_18` | `success` | ✅ reproduced |  | [log](crash/helloworld1_AnyMemo_18/carbon_log.txt) |
| 36 | crash | `helloworld1_AnyMemo_422` | `success` | ✅ reproduced |  | [log](crash/helloworld1_AnyMemo_422/carbon_log.txt) |
| 37 | crash | `helloworld1_AnyMemo_440` | `success` | ✅ reproduced |  | [log](crash/helloworld1_AnyMemo_440/carbon_log.txt) |
| 38 | crash | `hidroh_materialistic_1067` | `success` | ✅ reproduced | **as an ANR, not the reported crash** — see footnote | [log](crash/hidroh_materialistic_1067/carbon_log.txt) · [REPRODUCED-AS-ANR](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md) |
| 39 | crash | `javacafe01_PdfViewer_33` | `success` | ✅ reproduced |  | [log](crash/javacafe01_PdfViewer_33/carbon_log.txt) |
| 40 | crash | `k3b_APhotoManager_116` | `success` | ✅ reproduced |  | [log](crash/k3b_APhotoManager_116/carbon_log.txt) |
| 41 | crash | `kiwix_kiwix-android_990` | `success` | ✅ reproduced |  | [log](crash/kiwix_kiwix-android_990/carbon_log.txt) |
| 42 | crash | `koelleChristian_trickytripper_42` | `success` | ✅ reproduced |  | [log](crash/koelleChristian_trickytripper_42/carbon_log.txt) |
| 43 | crash | `lfuelling_lrkFM_44` | `success` | ✅ reproduced |  | [log](crash/lfuelling_lrkFM_44/carbon_log.txt) |
| 44 | crash | `mikepenz_FastAdapter_113` | `success` | ✅ reproduced |  | [log](crash/mikepenz_FastAdapter_113/carbon_log.txt) |
| 45 | crash | `mikepenz_FastAdapter_394` | `success` | ✅ reproduced |  | [log](crash/mikepenz_FastAdapter_394/carbon_log.txt) |
| 46 | crash | `milesmcc_LibreNews-Android_22` | `success` | ✅ reproduced |  | [log](crash/milesmcc_LibreNews-Android_22/carbon_log.txt) |
| 47 | crash | `milesmcc_LibreNews-Android_23` | `success` | ✅ reproduced |  | [log](crash/milesmcc_LibreNews-Android_23/carbon_log.txt) |
| 48 | crash | `milesmcc_LibreNews-Android_27` | `success` | ✅ reproduced |  | [log](crash/milesmcc_LibreNews-Android_27/carbon_log.txt) |
| 49 | crash | `mkulesh_microMathematics_39` | `success` | ✅ reproduced |  | [log](crash/mkulesh_microMathematics_39/carbon_log.txt) |
| 50 | crash | `moezbhatti_qksms_482` | `success` | ✅ reproduced |  | [log](crash/moezbhatti_qksms_482/carbon_log.txt) |
| 51 | crash | `moezbhatti_qksms_585` | `success` | ✅ reproduced |  | [log](crash/moezbhatti_qksms_585/carbon_log.txt) |
| 52 | crash | `moritz-herzog_Trainer-App_7` | `success` | ✅ reproduced |  | [log](crash/moritz-herzog_Trainer-App_7/carbon_log.txt) |
| 53 | crash | `mozilla-mobile_FirefoxLite_5085` | `success` | ✅ reproduced |  | [log](crash/mozilla-mobile_FirefoxLite_5085/carbon_log.txt) |
| 54 | crash | `netmackan_ATimeTracker_10` | `success` | ✅ reproduced |  | [log](crash/netmackan_ATimeTracker_10/carbon_log.txt) |
| 55 | crash | `netmackan_ATimeTracker_138` | `success` | ✅ reproduced |  | [log](crash/netmackan_ATimeTracker_138/carbon_log.txt) |
| 56 | crash | `netmackan_ATimeTracker_35` | `success` | ✅ reproduced |  | [log](crash/netmackan_ATimeTracker_35/carbon_log.txt) |
| 57 | crash | `opensudoku-android_OpenSudoku_173` | `success` | ✅ reproduced |  | [log](crash/opensudoku-android_OpenSudoku_173/carbon_log.txt) |
| 58 | crash | `pires_android-obd-reader_22` | `success` | ✅ reproduced |  | [log](crash/pires_android-obd-reader_22/carbon_log.txt) |
| 59 | crash | `ramack_ActivityDiary_285` | `success` | ✅ reproduced |  | [log](crash/ramack_ActivityDiary_285/carbon_log.txt) |
| 60 | crash | `rigid_Birthdroid_13` | `success` | ✅ reproduced |  | [log](crash/rigid_Birthdroid_13/carbon_log.txt) |
| 61 | crash | `robotmedia_droid-comic-viewer_12` | `success` | ✅ reproduced |  | [log](crash/robotmedia_droid-comic-viewer_12/carbon_log.txt) |
| 62 | crash | `samuelclay_NewsBlur_1053` | `success` | ✅ reproduced |  | [log](crash/samuelclay_NewsBlur_1053/carbon_log.txt) |
| 63 | crash | `thunderbird_thunderbird-android_3255` | `success` | ✅ reproduced |  | [log](crash/thunderbird_thunderbird-android_3255/carbon_log.txt) |
| 64 | crash | `ultrasonic_ultrasonic_187` | `success` | ✅ reproduced |  | [log](crash/ultrasonic_ultrasonic_187/carbon_log.txt) |
| 65 | crash | `vestrel00_android-dagger-butterknife-mvp_46` | `success` | ✅ reproduced |  | [log](crash/vestrel00_android-dagger-butterknife-mvp_46/carbon_log.txt) |
| 66 | crash | `vijai1996_screenrecorder_25` | `success` | ✅ reproduced |  | [log](crash/vijai1996_screenrecorder_25/carbon_log.txt) |
| 67 | crash | `vijai1996_screenrecorder_32` | `success` | ✅ reproduced |  | [log](crash/vijai1996_screenrecorder_32/carbon_log.txt) |
| 68 | crash | `vishnus_Olam_1` | `success` | ✅ reproduced |  | [log](crash/vishnus_Olam_1/carbon_log.txt) |
| 69 | crash | `vishnus_Olam_2` | `success` | ✅ reproduced |  | [log](crash/vishnus_Olam_2/carbon_log.txt) |
| 70 | crash | `y20k_transistor_149` | `success` | ✅ reproduced |  | [log](crash/y20k_transistor_149/carbon_log.txt) |
| 71 | crash | `y20k_transistor_63` | `success` | ✅ reproduced |  | [log](crash/y20k_transistor_63/carbon_log.txt) |
| 72 | crash | `zwieback_FamilyFinance_1` | `success` | ✅ reproduced |  | [log](crash/zwieback_FamilyFinance_1/carbon_log.txt) |
| 73 | non_crash | `Neamar_KISS_1481` | `success` | ✅ reproduced |  | [log](non_crash/Neamar_KISS_1481/carbon_log.txt) |
| 74 | non_crash | `PhenoApps_Field-Book_137` | `success` | ✅ reproduced |  | [log](non_crash/PhenoApps_Field-Book_137/carbon_log.txt) |
| 75 | non_crash | `Swati4star_Images-to-PDF_154` | `success` | ✅ reproduced |  | [log](non_crash/Swati4star_Images-to-PDF_154/carbon_log.txt) |
| 76 | non_crash | `VREMSoftwareDevelopment_WiFiAnalyzer_222` | `success` | ✅ reproduced |  | [log](non_crash/VREMSoftwareDevelopment_WiFiAnalyzer_222/carbon_log.txt) |
| 77 | non_crash | `alexstyl_Memento-Calendar_7` | `success` | ✅ reproduced |  | [log](non_crash/alexstyl_Memento-Calendar_7/carbon_log.txt) |
| 78 | non_crash | `andOTP_andOTP_567` | `success` | ✅ reproduced |  | [log](non_crash/andOTP_andOTP_567/carbon_log.txt) |
| 79 | non_crash | `andOTP_andOTP_580` | `success` | ✅ reproduced |  | [log](non_crash/andOTP_andOTP_580/carbon_log.txt) |
| 80 | non_crash | `andOTP_andOTP_638` | `success` | ✅ reproduced |  | [log](non_crash/andOTP_andOTP_638/carbon_log.txt) |
| 81 | non_crash | `ankidroid_Anki-Android_5753` | `success` | ✅ reproduced |  | [log](non_crash/ankidroid_Anki-Android_5753/carbon_log.txt) |
| 82 | non_crash | `barbeau_gpstest_404` | `success` | ✅ reproduced |  | [log](non_crash/barbeau_gpstest_404/carbon_log.txt) |
| 83 | non_crash | `beemdevelopment_Aegis_287` | `fail` | ❌ not reproduced | Genuine no-repro — language persisted correctly through restart (two runs) | [log](non_crash/beemdevelopment_Aegis_287/carbon_log.txt) · [NOT_REPRODUCIBLE](non_crash/beemdevelopment_Aegis_287/NOT_REPRODUCIBLE.md) |
| 84 | non_crash | `beemdevelopment_Aegis_415` | `success` | ✅ reproduced |  | [log](non_crash/beemdevelopment_Aegis_415/carbon_log.txt) |
| 85 | non_crash | `beemdevelopment_Aegis_473` | `success` | ✅ reproduced |  | [log](non_crash/beemdevelopment_Aegis_473/carbon_log.txt) |
| 86 | non_crash | `cohenadair_anglers-log_151` | `success` | ✅ reproduced |  | [log](non_crash/cohenadair_anglers-log_151/carbon_log.txt) |
| 87 | non_crash | `cohenadair_anglers-log_347` | `success` | ✅ reproduced |  | [log](non_crash/cohenadair_anglers-log_347/carbon_log.txt) |
| 88 | non_crash | `cohenadair_anglers-log_43` | `success` | ✅ reproduced |  | [log](non_crash/cohenadair_anglers-log_43/carbon_log.txt) |
| 89 | non_crash | `fr3ts0n_AndrOBD_144` | `success` | ✅ reproduced |  | [log](non_crash/fr3ts0n_AndrOBD_144/carbon_log.txt) |
| 90 | non_crash | `gsantner_markor_1020` | `success` | ✅ reproduced |  | [log](non_crash/gsantner_markor_1020/carbon_log.txt) |
| 91 | non_crash | `gsantner_markor_331` | `success` | ✅ reproduced |  | [log](non_crash/gsantner_markor_331/carbon_log.txt) |
| 92 | non_crash | `lfuelling_lrkFM_34` | `success` | ✅ reproduced |  | [log](non_crash/lfuelling_lrkFM_34/carbon_log.txt) |
| 93 | non_crash | `moezbhatti_qksms_1124` | `fail` | ❌ not reproduced | In-app Sound preference hidden on Android 8+; literal repro needs API ≤ 25 | [log](non_crash/moezbhatti_qksms_1124/carbon_log.txt) · [NOT_REPRODUCIBLE](non_crash/moezbhatti_qksms_1124/NOT_REPRODUCIBLE.md) |
| 94 | non_crash | `moezbhatti_qksms_1155` | `success` | ✅ reproduced |  | [log](non_crash/moezbhatti_qksms_1155/carbon_log.txt) |
| 95 | non_crash | `thunderbird_thunderbird-android_3971` | `success` | ✅ reproduced |  | [log](non_crash/thunderbird_thunderbird-android_3971/carbon_log.txt) |

Row count: 95 (72 crash + 23 non_crash). Every case in the folder is listed; there is no untested case.

## APK version verification

APK versions were verified against the bug reports (extracted from `AndroidManifest.xml`):

- `anki_5638`: 2.9.1 (matches report)
- `qksms_1124`: 3.1.3 (matches report)
- `osmeditor_637`: 0.9.10b1324 (matches report)

Version parity matters in both directions. For `anki_5638` the crash **was** reproduced on exactly the report-matching 2.9.1 build, which retires the earlier "fixed in 2.9.1" claim. For `qksms_1124` and `osmeditor_637`, version parity holds but the bug did not reproduce — and non-reproduction in a report-matching build still does not prove the bug is fixed. See each case's `NOT_REPRODUCIBLE.md` for the specific caveats.

## Caveats

1. **Failure to reproduce does not establish that a bug is fixed.** The 5 `NOT_REPRODUCIBLE.md` files are the authority; the table above only summarises them.
2. **One of the 90 is an ANR, not the reported crash.** `hidroh_materialistic_1067` — see the footnote above and [`crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md`](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md).
3. **90/95 follows a targeted retest pass**, not a single shot: the first wave was 70/95 and 20 of the 25 failures were converted with the per-case fixes tabulated above.
4. **Different dataset from the 100-bug gesture benchmark.** Not comparable to the root [`RESULTS.md`](../../RESULTS.md) tables.
5. **`ankidroid_Anki-Android_6432` differs across the two ReBL campaigns.** It is counted a CARBON **success** in [`../ReBL_Failed_Dataset/`](../ReBL_Failed_Dataset/) and in the root `RESULTS.md` challenge-set table (reproduced via a targeted manual retry), and **not reproduced** here (two harness retests timed out). Both stand as published; the run conditions differ. Neither 7/9 nor 90/95 moves.
6. **Per-case run logs are `carbon_log.txt`.** Each was originally named `<YYYYMMDD_HHMMSS_mmm>.log`, so timestamped filenames cited inside the carried-over `NOT_REPRODUCIBLE.md` and `REPRODUCED-AS-ANR.md` evidence files no longer resolve to a path in this folder; read them as run identifiers. One case, `crash/ankidroid_Anki-Android_6432`, keeps its earlier run at [`logs/20260926_220929_344.log`](crash/ankidroid_Anki-Android_6432/logs/20260926_220929_344.log).
7. **The 9 bugs in [`../ReBL_Failed_Dataset/`](../ReBL_Failed_Dataset/) are a curated subset of these 95**, kept separately on purpose because that folder is the artifact the paper cites. They are intentionally duplicated; do not deduplicate.

## Dataset provenance

Case inputs (reports, APKs, metadata) and how they were assembled: [`DATASET_PROVENANCE.md`](DATASET_PROVENANCE.md). Source snapshots and mapping tables: [`sources/`](sources/). Per-case setup notes and the 2026-09-26 re-verification pass: [`reverification/2026-09-26/REVERIFICATION.md`](reverification/2026-09-26/REVERIFICATION.md).

## Related documents

- [root `RESULTS.md`](../../RESULTS.md) — the 100-bug gesture benchmark and the 9-bug ReBL failure challenge set.
- [root `README.md`](../../README.md) — headline numbers and setup.
- [`../ReBL_Failed_Dataset/README.md`](../ReBL_Failed_Dataset/README.md) — the 9-bug challenge set, CARBON 7/9 vs ReBL 0/9.
