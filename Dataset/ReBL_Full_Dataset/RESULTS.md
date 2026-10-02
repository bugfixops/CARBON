# CARBON over the full ReBL Dataset

| | |
|---|---|
| Tool | CARBON |
| Model | `gemini-2.5-pro` |
| Cases tested | **95** (72 crash, 23 non-crash) |
| Reproduced | **90** (94.7%) |
| Not reproduced | **5** |
| Dates | 2026-09-26 to 2026-09-28 (the dates cited in the per-case evidence files) |

A different dataset from the 100-bug gesture benchmark; these numbers
are not comparable to the root [`RESULTS.md`](../../RESULTS.md)
tables. [`DATASET_PROVENANCE.md`](DATASET_PROVENANCE.md) indexes 96
input cases; 95 were tested and are the denominator here. The 96th,
`frigus02_car-report_43`, was never run and has no case folder.

**90 is the audited count; the logs self-report 91.** Across the 95
`carbon_log.txt` files, 91 end in `success`, 3 in `fail`, and 1
(`ankidroid_Anki-Android_6432`) has no verdict line because the run was
cut off by its time limit. The single difference between 91 and 90 is
`MarcusWolschon_osmeditor4android_637`, whose self-reported `success` is
rejected — see its row below. Every case's nominal and audited verdict is
in the [per-case table](#all-95-cases).
## The 5 that failed

| Case | Why it failed | Evidence |
|---|---|---|
| `crash/MarcusWolschon_osmeditor4android_637` | The agent reported `success`, but that claim is rejected: logcat has no FATAL EXCEPTION, no process-death marker, and the exception monitor that caught real crashes in sibling runs reported nothing. The app merely ended up on the launcher. APK 0.9.10.0.1324 matches the report. | [NOT_REPRODUCIBLE.md](crash/MarcusWolschon_osmeditor4android_637/NOT_REPRODUCIBLE.md) |
| `crash/ankidroid_Anki-Android_6432` | Two tests (45-minute and 1-hour limits) both ran out of time during the ~15-step note-type clone, card-add and multi-select setup without reaching the crash trigger; the 1-hour log ends `FINAL status=failed(timeout)` with no verdict. Harness and agent-capability limit. **A separate run of this bug did reproduce it** — the challenge-set run in [`../ReBL_Failed_Dataset/`](../ReBL_Failed_Dataset/RESULTS.md) records a crash dialog after the same setup, on a different build (`AnkiDroid-2.11.2.apk` there against this campaign's `Anki-Android_6432.apk`, manifest 2.12alpha2) and without a 1-hour cap. That run is not counted here; this campaign's own two attempts did not reach the trigger. | [NOT_REPRODUCIBLE.md](crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md) · [carbon_log.txt](crash/ankidroid_Anki-Android_6432/carbon_log.txt) |
| `crash/getodk_collect_360` | Reproduction requires Google OAuth sign-in, which the emulator cannot complete (no Play Services with valid credentials, and adb cannot drive the account auth flow). No test attempted. | [NOT_REPRODUCIBLE.md](crash/getodk_collect_360/NOT_REPRODUCIBLE.md) |
| `non_crash/beemdevelopment_Aegis_287` | Genuine no-repro, confirmed twice. With device locale fr-FR and the vault pre-created, the agent switched the language to English, force-stopped and relaunched, and the UI — settings screen included — stayed English. | [NOT_REPRODUCIBLE.md](non_crash/beemdevelopment_Aegis_287/NOT_REPRODUCIBLE.md) |
| `non_crash/moezbhatti_qksms_1124` | Not reproduced on API 30 with app v3.1.3: the notification channel was set to Silent and persisted. In v3.1.3 source, `NotificationPrefsActivity.onCreate` hides the in-app Sound preference on Android 8+ (`ringtone.setVisible(!hasOreo)`), so the in-app path the report used does not exist here. A literal reproduction needs API <= 25. | [NOT_REPRODUCIBLE.md](non_crash/moezbhatti_qksms_1124/NOT_REPRODUCIBLE.md) |

Failure to reproduce does not establish that a bug is fixed.
Each reason above says what blocked that run, not whether the bug
still exists upstream.

## All 95 cases

Nominal is the agent's own last verdict in `carbon_log.txt`. Audit is the
verdict this campaign publishes: a case is not reproduced exactly when its
directory holds a `NOT_REPRODUCIBLE.md`. The two differ for one case,
`MarcusWolschon_osmeditor4android_637`.

| Case | Group | Nominal log verdict | Audit verdict | Evidence |
|---|---|---|---|---|
| `alexstojda_soen390_36` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/alexstojda_soen390_36/carbon_log.txt) |
| `alexstyl_Memento-Calendar_169` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/alexstyl_Memento-Calendar_169/carbon_log.txt) |
| `andOTP_andOTP_135` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/andOTP_andOTP_135/carbon_log.txt) |
| `andOTP_andOTP_500` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/andOTP_andOTP_500/carbon_log.txt) |
| `andOTP_andOTP_569` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/andOTP_andOTP_569/carbon_log.txt) |
| `ankidroid_Anki-Android_4586` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/ankidroid_Anki-Android_4586/carbon_log.txt) |
| `ankidroid_Anki-Android_5638` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/ankidroid_Anki-Android_5638/carbon_log.txt) |
| `ankidroid_Anki-Android_6432` | crash | none (timed out) | ❌ not reproduced | [carbon_log.txt](crash/ankidroid_Anki-Android_6432/carbon_log.txt) · [NOT_REPRODUCIBLE.md](crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md) |
| `AntennaPod_AntennaPod_3245` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/AntennaPod_AntennaPod_3245/carbon_log.txt) |
| `ASU-CodeDevils_FlashCards_13` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/ASU-CodeDevils_FlashCards_13/carbon_log.txt) |
| `banderlabs_notepad_23` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/banderlabs_notepad_23/carbon_log.txt) |
| `beemdevelopment_Aegis_500` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/beemdevelopment_Aegis_500/carbon_log.txt) |
| `brodeurlv_fastnfitness_142` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/brodeurlv_fastnfitness_142/carbon_log.txt) |
| `CellularPrivacy_Android-IMSI-Catcher-Detector_816` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/CellularPrivacy_Android-IMSI-Catcher-Detector_816/carbon_log.txt) |
| `citiususc_calendula_134` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/citiususc_calendula_134/carbon_log.txt) |
| `cohenadair_anglers-log_9` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/cohenadair_anglers-log_9/carbon_log.txt) |
| `commons-app_apps-android-commons_2123` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/commons-app_apps-android-commons_2123/carbon_log.txt) |
| `dozingcat_AsciiCam_17` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/dozingcat_AsciiCam_17/carbon_log.txt) |
| `fdroid_fdroidclient_1821` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/fdroid_fdroidclient_1821/carbon_log.txt) |
| `gauravjot_android-noad-music-player_1` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/gauravjot_android-noad-music-player_1/carbon_log.txt) |
| `getodk_collect_1402` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_1402/carbon_log.txt) |
| `getodk_collect_1796` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_1796/carbon_log.txt) |
| `getodk_collect_2075` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_2075/carbon_log.txt) |
| `getodk_collect_2086` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_2086/carbon_log.txt) |
| `getodk_collect_2191` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_2191/carbon_log.txt) |
| `getodk_collect_2525` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_2525/carbon_log.txt) |
| `getodk_collect_3222` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/getodk_collect_3222/carbon_log.txt) |
| `getodk_collect_360` | crash | `fail` | ❌ not reproduced | [carbon_log.txt](crash/getodk_collect_360/carbon_log.txt) · [NOT_REPRODUCIBLE.md](crash/getodk_collect_360/NOT_REPRODUCIBLE.md) |
| `gsantner_markor_1698` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/gsantner_markor_1698/carbon_log.txt) |
| `gsantner_markor_194` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/gsantner_markor_194/carbon_log.txt) |
| `helloworld1_AnyMemo_18` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/helloworld1_AnyMemo_18/carbon_log.txt) |
| `helloworld1_AnyMemo_422` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/helloworld1_AnyMemo_422/carbon_log.txt) |
| `helloworld1_AnyMemo_440` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/helloworld1_AnyMemo_440/carbon_log.txt) |
| `hidroh_materialistic_1067` | crash | `success` | ✅ reproduced (as an ANR) | [carbon_log.txt](crash/hidroh_materialistic_1067/carbon_log.txt) · [REPRODUCED-AS-ANR.md](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md) |
| `javacafe01_PdfViewer_33` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/javacafe01_PdfViewer_33/carbon_log.txt) |
| `k3b_APhotoManager_116` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/k3b_APhotoManager_116/carbon_log.txt) |
| `kiwix_kiwix-android_990` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/kiwix_kiwix-android_990/carbon_log.txt) |
| `koelleChristian_trickytripper_42` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/koelleChristian_trickytripper_42/carbon_log.txt) |
| `lfuelling_lrkFM_44` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/lfuelling_lrkFM_44/carbon_log.txt) |
| `MarcusWolschon_osmeditor4android_637` | crash | `success` | ❌ not reproduced | [carbon_log.txt](crash/MarcusWolschon_osmeditor4android_637/carbon_log.txt) · [NOT_REPRODUCIBLE.md](crash/MarcusWolschon_osmeditor4android_637/NOT_REPRODUCIBLE.md) |
| `mikepenz_FastAdapter_113` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/mikepenz_FastAdapter_113/carbon_log.txt) |
| `mikepenz_FastAdapter_394` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/mikepenz_FastAdapter_394/carbon_log.txt) |
| `milesmcc_LibreNews-Android_22` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/milesmcc_LibreNews-Android_22/carbon_log.txt) |
| `milesmcc_LibreNews-Android_23` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/milesmcc_LibreNews-Android_23/carbon_log.txt) |
| `milesmcc_LibreNews-Android_27` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/milesmcc_LibreNews-Android_27/carbon_log.txt) |
| `mkulesh_microMathematics_39` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/mkulesh_microMathematics_39/carbon_log.txt) |
| `moezbhatti_qksms_482` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/moezbhatti_qksms_482/carbon_log.txt) |
| `moezbhatti_qksms_585` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/moezbhatti_qksms_585/carbon_log.txt) |
| `moritz-herzog_Trainer-App_7` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/moritz-herzog_Trainer-App_7/carbon_log.txt) |
| `mozilla-mobile_FirefoxLite_5085` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/mozilla-mobile_FirefoxLite_5085/carbon_log.txt) |
| `netmackan_ATimeTracker_10` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/netmackan_ATimeTracker_10/carbon_log.txt) |
| `netmackan_ATimeTracker_138` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/netmackan_ATimeTracker_138/carbon_log.txt) |
| `netmackan_ATimeTracker_35` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/netmackan_ATimeTracker_35/carbon_log.txt) |
| `opensudoku-android_OpenSudoku_173` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/opensudoku-android_OpenSudoku_173/carbon_log.txt) |
| `PhenoApps_Field-Book_145` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/PhenoApps_Field-Book_145/carbon_log.txt) |
| `PhenoApps_Field-Book_146` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/PhenoApps_Field-Book_146/carbon_log.txt) |
| `pires_android-obd-reader_22` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/pires_android-obd-reader_22/carbon_log.txt) |
| `ramack_ActivityDiary_285` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/ramack_ActivityDiary_285/carbon_log.txt) |
| `rigid_Birthdroid_13` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/rigid_Birthdroid_13/carbon_log.txt) |
| `robotmedia_droid-comic-viewer_12` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/robotmedia_droid-comic-viewer_12/carbon_log.txt) |
| `samuelclay_NewsBlur_1053` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/samuelclay_NewsBlur_1053/carbon_log.txt) |
| `SecUSo_privacy-friendly-weather_61` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/SecUSo_privacy-friendly-weather_61/carbon_log.txt) |
| `thunderbird_thunderbird-android_3255` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/thunderbird_thunderbird-android_3255/carbon_log.txt) |
| `ultrasonic_ultrasonic_187` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/ultrasonic_ultrasonic_187/carbon_log.txt) |
| `vestrel00_android-dagger-butterknife-mvp_46` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/vestrel00_android-dagger-butterknife-mvp_46/carbon_log.txt) |
| `vijai1996_screenrecorder_25` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/vijai1996_screenrecorder_25/carbon_log.txt) |
| `vijai1996_screenrecorder_32` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/vijai1996_screenrecorder_32/carbon_log.txt) |
| `vishnus_Olam_1` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/vishnus_Olam_1/carbon_log.txt) |
| `vishnus_Olam_2` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/vishnus_Olam_2/carbon_log.txt) |
| `y20k_transistor_149` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/y20k_transistor_149/carbon_log.txt) |
| `y20k_transistor_63` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/y20k_transistor_63/carbon_log.txt) |
| `zwieback_FamilyFinance_1` | crash | `success` | ✅ reproduced | [carbon_log.txt](crash/zwieback_FamilyFinance_1/carbon_log.txt) |
| `alexstyl_Memento-Calendar_7` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/alexstyl_Memento-Calendar_7/carbon_log.txt) |
| `andOTP_andOTP_567` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/andOTP_andOTP_567/carbon_log.txt) |
| `andOTP_andOTP_580` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/andOTP_andOTP_580/carbon_log.txt) |
| `andOTP_andOTP_638` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/andOTP_andOTP_638/carbon_log.txt) |
| `ankidroid_Anki-Android_5753` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/ankidroid_Anki-Android_5753/carbon_log.txt) |
| `barbeau_gpstest_404` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/barbeau_gpstest_404/carbon_log.txt) |
| `beemdevelopment_Aegis_287` | non_crash | `fail` | ❌ not reproduced | [carbon_log.txt](non_crash/beemdevelopment_Aegis_287/carbon_log.txt) · [NOT_REPRODUCIBLE.md](non_crash/beemdevelopment_Aegis_287/NOT_REPRODUCIBLE.md) |
| `beemdevelopment_Aegis_415` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/beemdevelopment_Aegis_415/carbon_log.txt) |
| `beemdevelopment_Aegis_473` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/beemdevelopment_Aegis_473/carbon_log.txt) |
| `cohenadair_anglers-log_151` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/cohenadair_anglers-log_151/carbon_log.txt) |
| `cohenadair_anglers-log_347` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/cohenadair_anglers-log_347/carbon_log.txt) |
| `cohenadair_anglers-log_43` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/cohenadair_anglers-log_43/carbon_log.txt) |
| `fr3ts0n_AndrOBD_144` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/fr3ts0n_AndrOBD_144/carbon_log.txt) |
| `gsantner_markor_1020` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/gsantner_markor_1020/carbon_log.txt) |
| `gsantner_markor_331` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/gsantner_markor_331/carbon_log.txt) |
| `lfuelling_lrkFM_34` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/lfuelling_lrkFM_34/carbon_log.txt) |
| `moezbhatti_qksms_1124` | non_crash | `fail` | ❌ not reproduced | [carbon_log.txt](non_crash/moezbhatti_qksms_1124/carbon_log.txt) · [NOT_REPRODUCIBLE.md](non_crash/moezbhatti_qksms_1124/NOT_REPRODUCIBLE.md) |
| `moezbhatti_qksms_1155` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/moezbhatti_qksms_1155/carbon_log.txt) |
| `Neamar_KISS_1481` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/Neamar_KISS_1481/carbon_log.txt) |
| `PhenoApps_Field-Book_137` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/PhenoApps_Field-Book_137/carbon_log.txt) |
| `Swati4star_Images-to-PDF_154` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/Swati4star_Images-to-PDF_154/carbon_log.txt) |
| `thunderbird_thunderbird-android_3971` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/thunderbird_thunderbird-android_3971/carbon_log.txt) |
| `VREMSoftwareDevelopment_WiFiAnalyzer_222` | non_crash | `success` | ✅ reproduced | [carbon_log.txt](non_crash/VREMSoftwareDevelopment_WiFiAnalyzer_222/carbon_log.txt) |
