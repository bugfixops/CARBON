# MarcusWolschon_osmeditor4android_637 — DOES NOT REPRODUCE

**Bug report claim:** In Vespucci 0.9.10b1324, configuring the Validator
(delete all entries except one with Key=shop/Value=*/Max age=0) then using
Transfer → "Download current view" causes a FATAL EXCEPTION crash.

**APK version verified:** 0.9.10.0.1324 (matches bug report's 0.9.10b1324 —
extracted from AndroidManifest.xml string pool).

**What we did (v4 retest with 1-hour timeout, 2026-09-27):**
- Agent completed the full validator configuration via UI
- Deleted all entries except one, set Key=shop, Value=*, Max age=0
- Navigated back to map, opened Transfer → "Download current view"

**Agent's final verdict (from run log `20260927_062814_760.log`):**
> "I have followed all the steps in the bug report. The final step was to
> download the current view, which the bug report states should cause the app
> to crash. After I clicked 'Download current view', a UI element briefly
> appeared and then disappeared, and the app returned to the main map screen.
> The app did not crash."

**Note:** The bug report itself mentions the fix landed in 0.9.10b1325, but
our 0.9.10b1324 build also does not crash. The trigger may be device-specific
(originally reported on Samsung Galaxy A3, Android 6.0.1).

**Conclusion:** The crash does not reproduce in the tested version/environment.
Not a test failure.
