# moezbhatti_qksms_1124 — NOT REPRODUCED (rerun consistent with v4)

**Bug report claim:** In QKSMS 3.1.3 on Android 6.0.1, setting notification Sound to "None" does not save — it reverts to the previous value.

**APK version verified:** 3.1.3 (matches bug report).

**What we did (wave-2 retest, log `20260928_000421_532.log`, 2026-09-28):** Agent set the notification channel to "Silent", navigated away and back — the setting persisted, did not revert.

**Why the in-app path is unreachable on API 30 (verified in v3.1.3 source):** `NotificationPrefsActivity.onCreate` hides the in-app Sound ("ringtone") preference on Android 8+ (`ringtone.setVisible(!hasOreo)`); sound config is routed to the OS notification channel. The bug was reported on Android 6.0.1 where the in-app preference existed.

**Conclusion:** Not reproduced under tested conditions (API 30, app v3.1.3). A literal reproduction would require API ≤ 25. Cause remains unresolved — failure to reproduce does not establish the bug is fixed.
