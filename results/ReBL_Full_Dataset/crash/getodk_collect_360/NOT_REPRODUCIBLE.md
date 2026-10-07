# getodk_collect_360 — SKIPPED

**Reason:** Requires Google OAuth login.

The bug report's reproduction steps require signing in with a Google account.
The emulator cannot complete Google OAuth (no Play Services with valid
credentials, and adb does not allow the account authentication flow).

**Decision (2026-09-26):** cases that need a Google sign-in are skipped.

No retest was attempted. This is an environment limitation, not a bug fix.
