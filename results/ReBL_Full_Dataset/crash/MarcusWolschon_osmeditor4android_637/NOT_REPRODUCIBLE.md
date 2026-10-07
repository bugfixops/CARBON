# MarcusWolschon_osmeditor4android_637 — NOT REPRODUCED (agent overclaimed; no crash evidence)

**Bug report claim:** In Vespucci 0.9.10b1324, configuring the Validator (delete all entries except one with Key=shop/Value=*/Max age=0) then using Transfer → "Download current view" causes a FATAL EXCEPTION crash.

**APK version verified:** 0.9.10.0.1324 (matches bug report's 0.9.10b1324).

**What we did (wave-2 retest, 90-min timeout, log `20260928_000418_597.log`, 2026-09-28):** Agent configured the Validator exactly as specified and clicked "Download current view".

**Agent's final verdict:** `success` — "the app crashed and returned to the home screen."

**Why that verdict is rejected:** The log shows the app on the home screen (NexusLauncherActivity) after the click, but logcat contains **no FATAL EXCEPTION**, **no process-death marker**, and the logcat exception monitor (which did catch real crashes in sibling runs) reported nothing. The agent itself noted mid-run that the app "did not crash as expected" and the download may have "failed silently". An app ending up on the home screen without any crash signature is not a reproduction of the reported FATAL EXCEPTION crash.

**Conclusion:** Not reproduced under tested conditions. "Fixed" is not established.
