# beemdevelopment_Aegis_287 — NO-REPRO (confirmed by two independent runs)

**Bug report claim:** After setting language to French then back to English, restarting the app reverts the UI to French.

**What we did:**
- v6 retest (log `20260927_051555_043.log`): device locale fr-FR via zygote restart, vault pre-created (password "password"). Agent unlocked vault, changed language to English, force-stopped, relaunched, unlocked again — UI stayed English.
- Wave-2 retest (log `20260928_000444_334.log`, 2026-09-28): identical setup. Agent verified the main screen, overflow menu, and settings screen (which explicitly shows language still set to "English") after restart — UI remained English.

**Conclusion:** Language setting persists correctly through restart. Genuine no-repro, now confirmed twice.
