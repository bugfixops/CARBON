# ReBL-dataset CARBON Retest Campaign — Failure-Fix Results

**Date:** 2026-09-26 to 2026-09-28  
**Model:** gemini-2.5-pro  
**Status:** merged to `main`; the campaign now lives at `Dataset/ReBL_Full_Dataset/`

## Summary

After the initial wave (70/95 success, 73.7%), all 25 failures were individually
retested with targeted fixes (custom APKs, pre-setup scripts, improved agent hints,
harness actions like `rapid_click` and `tap_then_swipe`, API level adjustments).

**Final tally: 90/95 (94.7%)** — 20 conversions.

The tally is reconciled against the committed per-case evidence in this directory:
95 executed cases minus the 5 remaining `NOT_REPRODUCIBLE.md` files = 90 reproduced.
One of those 90 — `hidroh_materialistic_1067` — is counted as reproduced **as an ANR**,
not as the originally reported crash; see the footnote below.

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
| hidroh_materialistic_1067 | Wave-2 retest — timing/race repro; reproduced AS AN ANR, not the reported crash [^anr] |

[^anr]: **`hidroh_materialistic_1067` is counted as reproduced as an ANR, not as the
reported crash.** The wave-2 retest triggered a genuine "Materialistic isn't responding"
ANR dialog (Wait / Close app, confirmed in the UI dump) after save-then-swipe during
loading, so the timing race is real and was provoked by the reported interaction.
However, logcat contains **no FATAL EXCEPTION** for that run: the manifestation was a
UI-thread freeze, not the reported crash, and the originally reported crash signature
remains unconfirmed. Full evidence: `crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md`.

## Remaining 5 (not reproduced)

**Not reproduced under the tested conditions; causes remain partly unresolved.**
Failure to reproduce does not establish that a bug is fixed. See each case
folder's `NOT_REPRODUCIBLE.md` for the full evidence and caveats.

| Case | Status |
|------|--------|
| getodk_collect_360 | Skipped — reproduction requires Google OAuth sign-in, which the emulator cannot complete (no Play Services with valid credentials; adb cannot drive the account auth flow). No retest attempted, per the 2026-09-26 directive to skip Google-login APKs. Environment limitation, not a fix. |
| beemdevelopment_Aegis_287 | No-repro, confirmed by two independent runs (v6 and wave-2): with device locale fr-FR and the vault pre-created, the agent switched the language to English, force-stopped and relaunched, and the UI — including the settings screen — stayed English. Language persists correctly through restart. |
| ankidroid_Anki-Android_6432 | Setup failure — two retests (45-minute and 1-hour) both timed out during the ~15-step custom note-type / clone / add-cards / multi-select setup without reaching the crash trigger. Harness and agent-capability limitation, not confirmation of a fix. |
| moezbhatti_qksms_1124 | Not reproduced on API 30 with app v3.1.3: the notification channel was set to "Silent" and persisted. Verified in v3.1.3 source that `NotificationPrefsActivity.onCreate` hides the in-app Sound preference on Android 8+ (`ringtone.setVisible(!hasOreo)`), routing sound config to the OS channel; the bug was reported on Android 6.0.1 where that in-app preference existed. A literal reproduction would require API ≤ 25. |
| MarcusWolschon_osmeditor4android_637 | Not reproduced — the agent's own `success` verdict is **rejected**. In the wave-2 retest (90-minute timeout) the app ended up on the launcher after "Download current view", but logcat shows no FATAL EXCEPTION, no process-death marker, and the exception monitor (which caught real crashes in sibling runs) reported nothing. APK version 0.9.10.0.1324 matches the report. |

## APK Version Verification

APK versions were verified against the bug reports (extracted from
AndroidManifest.xml):
- anki_5638: 2.9.1 (matches report)
- qksms_1124: 3.1.3 (matches report)
- osmeditor_637: 0.9.10b1324 (matches report)

Version parity matters in both directions. For `anki_5638` the crash **was** reproduced
on exactly the report-matching 2.9.1 build, which retires the earlier "fixed in 2.9.1"
claim. For `qksms_1124` and `osmeditor_637`, version parity holds but the bug did not
reproduce — and non-reproduction in a report-matching build still does not prove the bug
is fixed. See each case's notes for the specific caveats.

## Run logs

Each case's run log is now `carbon_log.txt`. It was originally named
`<YYYYMMDD_HHMMSS_mmm>.log`, so the filenames cited inside the carried-over
`NOT_REPRODUCIBLE.md` and `REPRODUCED-AS-ANR.md` evidence files resolve through
`LOG_FILENAME_MAP.tsv` in this directory. One case,
`crash/ankidroid_Anki-Android_6432`, produced two runs: the newer is `carbon_log.txt`
and the earlier is preserved at `crash/ankidroid_Anki-Android_6432/logs/20260926_220929_344.log`.
Per-shard machine-readable summaries from the 10-way sharded wave are in `_batch_summaries/`.
