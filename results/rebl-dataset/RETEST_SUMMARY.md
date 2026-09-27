# ReBL-dataset CARBON Retest Campaign — Failure-Fix Results

**Date:** 2026-09-26 to 2026-09-27  
**Model:** gemini-2.5-pro  
**Branch:** rebl-carbon-test

## Summary

After the initial wave (70/95 success, 73.7%), all 25 failures were individually
retested with targeted fixes (custom APKs, pre-setup scripts, improved agent hints,
harness actions like `rapid_click` and `tap_then_swipe`, API level adjustments).

**Final tally: 88/95 (92.6%)** — 18 conversions.

## Conversions (18)

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

## Remaining 7 (not passing)

| Case | Reason |
|------|--------|
| getodk_collect_360 | Skipped — requires Google OAuth (user directive) |
| beemdevelopment_Aegis_287 | Confirmed no-repro — vault and language settings work correctly |
| ankidroid_Anki-Android_5638 | Bug fixed in 2.9.1 (PR #5670 already merged) |
| moezbhatti_qksms_1124 | Bug fixed in 3.1.3 (setting saves correctly) |
| MarcusWolschon_osmeditor4android_637 | Does not reproduce in 0.9.10b1324 |
| hidroh_materialistic_1067 | Race condition won't trigger reliably |
| ankidroid_Anki-Android_6432 | Agent cannot complete complex multi-step setup |

## APK Version Verification

All "fixed" cases were verified to use the exact versions from the bug reports:
- anki_5638: 2.9.1 (matches report)
- qksms_1124: 3.1.3 (matches report)
- osmeditor_637: 0.9.10b1324 (matches report)

The bugs are genuinely fixed in those builds, not version mismatches.
