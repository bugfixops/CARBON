# ankidroid_Anki-Android_5638 — NOT REPRODUCED (cause unresolved)

**Bug report claim:** Entering `&bsol;` (6 chars) in any card field and saving
causes AnkiDroid to crash. Reopening and opening the card browser crashes again.

**APK version verified:** 2.9.1 (matches bug report — extracted from
AndroidManifest.xml string pool).

**What we did:**
- v1-v4: Agent tried entering `&bsol;`, `&#x5c;`, `&#92;` via UI. The app
  consistently showed "Error saving note" instead of crashing.
- v5 (log `20260927_062910_071.log`): Pre-setup UI-automated a normal card
  creation to initialize the database, then directly injected a corrupt card
  (with `&bsol;` in the Front field) into the SQLite database, bypassing UI
  validation. Agent opened the card browser — no crash, "0 cards shown."

**Agent's final verdict:**
> "I have now followed the bug report's instructions precisely... However, the
> screen is stable, has not crashed, and displays '0 cards shown.' This
> strongly indicates that the app is no longer vulnerable to this crash."

**Important correction:** The earlier claim that "PR #5670 is already merged
into 2.9.1" was **wrong**. PR #5670 merged December 27, 2019; 2.9.1 was
released October 15, 2019. The tagged 2.9.1 source still contains the
vulnerable expression. The "Error saving note" behavior needs investigation —
it does not prove the fix is present. The dataset APK may differ from upstream
2.9.1, or another validation may be at play.

**Conclusion:** Not reproduced under tested conditions. Cause remains
unresolved.
