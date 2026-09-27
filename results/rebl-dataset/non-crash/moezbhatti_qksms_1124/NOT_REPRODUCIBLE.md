# moezbhatti_qksms_1124 — NOT REPRODUCED (in-app Sound preference unreachable on API 30)

**Bug report claim:** In QKSMS 3.1.3 on Android 6.0.1, setting notification
Sound to "None" does not save — it reverts to the previous value. The original
discussion credits the fix in **3.2.2**, not 3.1.3.

**APK version verified:** 3.1.3 (matches bug report — extracted from
AndroidManifest.xml string pool).

**What we did (v4 retest, 1-hour timeout, API 30, log `20260927_181950_731.log`):**
- Agent navigated QKSMS's own Settings → Notifications (in-app
  `NotificationPrefsActivity`, visited 6 times).
- On API 30 that screen shows only Notifications / Notification previews /
  QK Reply rows — **no Sound row**.
- Agent continued via the "Notifications" row, which opens the OS notification
  channel settings; set channel Sound to "None" via the system sound picker,
  saved, navigated away and back — "None" persisted.

**Agent's final verdict:** fail (bug not reproduced) — "The setting correctly
remained as 'None'. The buggy behavior, where the setting reverts to its
previous value, did not occur."

**Why the in-app path is unreachable on API 30 (verified in v3.1.3 source):**
`NotificationPrefsActivity.onCreate` contains
```kotlin
val hasOreo = Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
...
ringtone.setVisible(!hasOreo)
```
so on Android 8+ the app deliberately hides its in-app Sound ("ringtone")
preference and routes sound configuration to the OS notification channel.
The bug was reported on Android 6.0.1, where the in-app preference existed.

**Conclusion:** Not reproduced under tested conditions (API 30, app v3.1.3).
The reported in-app Sound preference does not exist on Android 8+ by the
app's own design; the OS-level equivalent persists "None" correctly. A literal
reproduction of the reported bug would require API ≤ 25. Cause remains
unresolved — failure to reproduce does not establish the bug is fixed.
