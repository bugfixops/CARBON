# moezbhatti_qksms_1124 — BUG FIXED IN TESTED VERSION

**Bug report claim:** In QKSMS 3.1.3, setting notification Sound to "None" does
not save — it reverts to the previous value.

**APK version verified:** 3.1.3 (matches bug report — extracted from
AndroidManifest.xml string pool; also confirmed via apktool).

**What we did (v3 retest with 1-hour timeout, 2026-09-27):**
- Agent navigated to Settings → Notifications → Sound (Advanced section)
- Selected "None", saved, navigated back
- Re-entered Notifications settings to verify the saved value

**Agent's final verdict (from run log `20260927_062826_534.log`):**
> "I have followed all the steps outlined in the bug report. 1. I navigated
> to Settings -> Notifications. 2. I tapped on Sound (within the Advanced
> section). 3. I selected 'None' and saved the setting. 4. I navigated back
> to the previous screen. 5. I re-entered the Notifications settings and
> expanded the Advanced section to check the value. The current screen shows
> that the 'Sound' setting is 'None'. The bug report states that the issue
> is the setting reverting to its previous value and *not*..."

**Conclusion:** The setting saves correctly as "None". The bug is fixed in
3.1.3. Not a test failure.
