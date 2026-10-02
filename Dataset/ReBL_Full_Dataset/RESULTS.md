# CARBON over the full ReBL Dataset

| | |
|---|---|
| Tool | CARBON |
| Model | `gemini-2.5-pro` |
| Cases tested | **95** |
| Reproduced | **90** |
| Not reproduced | **5** |

A different dataset from the 100-bug gesture benchmark; these numbers
are not comparable to the root [`RESULTS.md`](../../RESULTS.md)
tables. [`DATASET_PROVENANCE.md`](DATASET_PROVENANCE.md) indexes 96
input cases; 95 were tested and are the denominator here. The 96th,
`frigus02_car-report_43`, was never run and has no case folder.

The 90 is not a single-shot rate. The initial wave reproduced **70 of
95** (73.7%); its 25 failures were then individually retested with
targeted fixes — report-matching APK builds, pre-setup scripts,
API-level corrections, loop-guard tuning, extra harness actions — and
**20 converted**, leaving the 5 below.

> **`hidroh_materialistic_1067` counts toward the 90 as an ANR, not as
> the reported crash.** The retest triggered a genuine "Materialistic
> isn't responding" dialog after save-then-swipe during loading, so
> the timing race is real. But logcat contains **no FATAL EXCEPTION**
> for that run: the manifestation was a UI-thread freeze, and the
> originally reported crash signature remains unconfirmed. Evidence:
> [`crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md`](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md).

## The 5 that failed

| Case | Why it failed | Evidence |
|---|---|---|
| `crash/MarcusWolschon_osmeditor4android_637` | The agent reported `success`, but that claim is rejected: logcat has no FATAL EXCEPTION, no process-death marker, and the exception monitor that caught real crashes in sibling runs reported nothing. The app merely ended up on the launcher. APK 0.9.10.0.1324 matches the report. | [NOT_REPRODUCIBLE.md](crash/MarcusWolschon_osmeditor4android_637/NOT_REPRODUCIBLE.md) |
| `crash/ankidroid_Anki-Android_6432` | Two retests (45-minute and 1-hour limits) both ran out of time during the ~15-step note-type clone, card-add and multi-select setup without reaching the crash trigger. Harness and agent-capability limit. | [NOT_REPRODUCIBLE.md](crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md) |
| `crash/getodk_collect_360` | Reproduction requires Google OAuth sign-in, which the emulator cannot complete (no Play Services with valid credentials, and adb cannot drive the account auth flow). No retest attempted. | [NOT_REPRODUCIBLE.md](crash/getodk_collect_360/NOT_REPRODUCIBLE.md) |
| `non_crash/beemdevelopment_Aegis_287` | Genuine no-repro, confirmed twice. With device locale fr-FR and the vault pre-created, the agent switched the language to English, force-stopped and relaunched, and the UI — settings screen included — stayed English. | [NOT_REPRODUCIBLE.md](non_crash/beemdevelopment_Aegis_287/NOT_REPRODUCIBLE.md) |
| `non_crash/moezbhatti_qksms_1124` | Not reproduced on API 30 with app v3.1.3: the notification channel was set to Silent and persisted. In v3.1.3 source, `NotificationPrefsActivity.onCreate` hides the in-app Sound preference on Android 8+ (`ringtone.setVisible(!hasOreo)`), so the in-app path the report used does not exist here. A literal reproduction needs API <= 25. | [NOT_REPRODUCIBLE.md](non_crash/moezbhatti_qksms_1124/NOT_REPRODUCIBLE.md) |

Failure to reproduce does not establish that a bug is fixed.
Each reason above says what blocked that run, not whether the bug
still exists upstream.
