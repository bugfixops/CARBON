# beemdevelopment_Aegis_287 — NO-REPRO (v6 log published)

**Bug report claim:** After setting language to French then back to English,
restarting the app reverts the UI to French.

**What we did (v6 retest, log `20260927_051555_043.log`, 2026-09-27):**
- Pre-setup set the device locale to fr-FR via zygote restart
- Pre-created the vault via UI automation (password: "password")
- Agent unlocked the vault, changed language to English, force-stopped the app
- Relaunched the app, unlocked the vault again

**Agent's final verdict:**
> "I have unlocked the vault and am now on the main screen. According to the
> bug report, if the bug is present, the UI should have reverted to French
> after the restart. Let's examine the current UI: - The main text on the
> screen is 'No entries found' and 'There are no codes to be shown...'. This
> is English. - The toolbar options include 'Filter' and 'More options'.
> This is also English. The app's UI is in English, which means the language
> setting I applied has persisted correctly..."

**Note:** Earlier retest logs (v2–v5) ended in a vault-setup blocker and could
not confirm language persistence. The v6 log above is the evidence for the
no-repro conclusion.

**Conclusion:** Language setting persists correctly through restart. Genuine
no-repro.
