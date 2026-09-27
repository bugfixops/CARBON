# MarcusWolschon_osmeditor4android_637 — NOT REPRODUCIBLED (incomplete evidence)

**Bug report claim:** In Vespucci 0.9.10b1324, configuring the Validator
(delete all entries except one with Key=shop/Value=*/Max age=0) then using
Transfer → "Download current view" causes a FATAL EXCEPTION crash.

**APK version verified:** 0.9.10.0.1324 (matches bug report's 0.9.10b1324).

**What we did:**
- Wave log: timed out before completing the download trigger; contained
  repeated API rate-limit errors. Inconclusive.
- v4 retest (1-hour timeout, log `20260927_062814_760.log`): Agent completed
  the full validator configuration and triggered "Download current view."

**Agent's final verdict (v4):**
> "After I clicked 'Download current view', a UI element briefly appeared and
> then disappeared, and the app returned to the main map screen. The app did
> not crash."

**Caveat:** The wave-run log is inconclusive (timeout + rate limits). The v4
log shows a clean no-crash run, but the trigger is device-specific in the
original report (Samsung Galaxy A3, Android 6.0.1).

**Conclusion:** Not reproduced under tested conditions. "Fixed" is not
established.
