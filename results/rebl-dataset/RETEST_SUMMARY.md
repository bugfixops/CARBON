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

## Remaining 7 (not reproduced)

**Not reproduced under the tested conditions; causes remain partly unresolved.**
Failure to reproduce does not establish that a bug is fixed. See each case
folder's `NOT_REPRODUCIBLE.md` for the full evidence and caveats.

| Case | Status |
|------|--------|
| getodk_collect_360 | Skipped — requires Google OAuth (environment blocker; original attempt ran and failed on this prerequisite) |
| beemdevelopment_Aegis_287 | No-repro — v6 retest confirmed language persists correctly (see published v6 log) |
| ankidroid_Anki-Android_5638 | Not reproduced — "Error saving note" needs investigation; the earlier "fixed in 2.9.1" claim was wrong (PR #5670 merged Dec 2019, after 2.9.1's Oct 2019 release) |
| moezbhatti_qksms_1124 | Not reproduced — possible settings-path mismatch (agent tested system notification channels, not the app's in-app path; original fix credited in 3.2.2) |
| MarcusWolschon_osmeditor4android_637 | Not reproduced — wave log was inconclusive (timeout + rate limits); v4 retest showed no crash but trigger may be device-specific |
| hidroh_materialistic_1067 | Not reproduced — plausibly timing-sensitive; race window not hittable in emulator |
| ankidroid_Anki-Android_6432 | Setup failure — agent could not complete the ~15-step card/note-type setup within time limits |

## APK Version Verification

APK versions were verified against the bug reports (extracted from
AndroidManifest.xml):
- anki_5638: 2.9.1 (matches report)
- qksms_1124: 3.1.3 (matches report)
- osmeditor_637: 0.9.10b1324 (matches report)

Version parity holds, but non-reproduction in the tested build does not prove
the bug is fixed — see per-case notes for the specific caveats.
