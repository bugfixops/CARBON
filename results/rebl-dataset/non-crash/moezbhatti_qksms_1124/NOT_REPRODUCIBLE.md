# moezbhatti_qksms_1124 — NOT REPRODUCED (possible settings-path mismatch)

**Bug report claim:** In QKSMS 3.1.3 on Android 6.0.1, setting notification
Sound to "None" does not save — it reverts to the previous value. The original
discussion credits the fix in **3.2.2**, not 3.1.3.

**APK version verified:** 3.1.3 (matches bug report — extracted from
AndroidManifest.xml string pool).

**What we did (v3, 1-hour timeout, log `20260927_062826_534.log`):**
- Agent navigated to Settings → Notifications → Sound, selected "None",
  saved, navigated back, re-entered to verify.

**Agent's final verdict:**
> "The current screen shows that the 'Sound' setting is 'None'."

**Problem with this test:** The agent operated Android's notification-channel
settings (system-level), not QKSMS's own in-app notification settings path
described in the original report. Seeing "None" persist in the system channel
does not establish that 3.1.3 fixed the original in-app bug.

**Conclusion:** Not reproduced under tested conditions. The test may have
targeted the wrong settings path. Cause remains unresolved.
