# CARBON over the ReBL Failure Challenge Set

| | |
|---|---|
| Tool | CARBON |
| Model | `gemini-2.5-pro` |
| Cases tested | **9** |
| Reproduced | **7** |
| Not reproduced | **2** |

The 9 bug reports ReBL (ISSTA'24) §5.1.1 names as its own reproduction
failures, re-crawled from GitHub and rebuilt as a standalone set. **ReBL
is 0/9 here by construction** — every case is a documented ReBL failure,
not a fresh ReBL run. These 9 are a separate set from the 100-bug gesture
benchmark and are not counted in its totals; the same figures appear in
the root [`RESULTS.md`](../../RESULTS.md).

**These 9 are a subset of the 95-case full ReBL campaign, not an addition
to it.** All 9 case directories also exist in
[`../ReBL_Full_Dataset/`](../ReBL_Full_Dataset/RESULTS.md), so this 7/9
and that campaign's 90/95 describe overlapping cases and must not be
added together. The runs are different runs: these are targeted manual
re-runs against this curated set, so one case —
`ankidroid_Anki-Android_6432` — lands on a different verdict in each, and
both rows say why.

Per-case evidence sits in `<type>/<Owner>_<Repo>_<Issue>/`: the bug
report, CARBON's log, a run note, and an annotated screenshot.

## All 9 cases

| Case | Type | CARBON | What decided it | Evidence |
|---|---|---|---|---|
| `alexstyl_Memento-Calendar_169` | crash | ✅ | Reached the custom date-picker wheels through `swipe_region` on screenshot coordinates after hierarchy-level scrolling failed; February 31 fired a FATAL EXCEPTION. | [carbon_log.txt](crash/alexstyl_Memento-Calendar_169/carbon_log.txt) |
| `ankidroid_Anki-Android_6432` | crash | ✅ | Inferred the preparation the 3-step report omits (clone a note type, add two cards, reach multi-select), then the type change fired the crash dialog. 62 commands, 1520.7s, on `AnkiDroid-2.11.2.apk`. **The full ReBL campaign counts this case as not reproduced** — its two retests (45-minute and 1-hour caps, on `Anki-Android_6432.apk`, manifest 2.12alpha2) timed out during the same setup. Different build, different time budget, different outcome; see [`../ReBL_Full_Dataset/RESULTS.md`](../ReBL_Full_Dataset/RESULTS.md) and its [`NOT_REPRODUCIBLE.md`](../ReBL_Full_Dataset/crash/ankidroid_Anki-Android_6432/NOT_REPRODUCIBLE.md). | [carbon_log.txt](crash/ankidroid_Anki-Android_6432/carbon_log.txt) · [note.txt](crash/ankidroid_Anki-Android_6432/note.txt) |
| `getodk_collect_360` | crash | ❌ | **Cross-app OAuth blocker.** Set the platform to Google Drive and opened the account selector, then halted at "No Google Account Selected!" — the emulator has no Google account and the account-auth flow cannot be driven through UI automation, so the My Drive screen where the crash occurs was never reached. 11 turns, 303s. The same limitation ReBL reports. | [carbon_log.txt](crash/getodk_collect_360/carbon_log.txt) · [note.txt](crash/getodk_collect_360/note.txt) |
| `MarcusWolschon_osmeditor4android_637` | crash | ❌ | **Data-state precondition not met.** The crash needs OSM data already downloaded before the validator edit; the in-run tile download never completed inside the run window. Four scenarios over 48 turns (1507s), including the empty-list and re-visit-without-save variants, all ended with no crash. `set_text` — ReBL's stated blocker on this app — worked, so the two tools fail here for different reasons. The full ReBL campaign also records this case as not reproduced, by a different route: there the agent claimed `success` and the claim was rejected on audit. | [carbon_log.txt](crash/MarcusWolschon_osmeditor4android_637/carbon_log.txt) · [note.txt](crash/MarcusWolschon_osmeditor4android_637/note.txt) |
| `cohenadair_anglers-log_347` | non_crash | ✅ | Read the alert text "Start date must come before end date." verbatim after editing a trip's start date past its end date. | [carbon_log.txt](non_crash/cohenadair_anglers-log_347/carbon_log.txt) |
| `PhenoApps_Field-Book_137` | non_crash | ✅ | All four Zebra Label spinners reported `DISABLED` in the hierarchy dump, matching the report's "unable to change the label size". | [carbon_log.txt](non_crash/PhenoApps_Field-Book_137/carbon_log.txt) |
| `lfuelling_lrkFM_34` | non_crash | ✅ | Moved the file, navigated into a *different* folder before pasting, and confirmed the target stayed empty — the same-folder confusion ReBL reports is avoided. | [carbon_log.txt](non_crash/lfuelling_lrkFM_34/carbon_log.txt) |
| `moezbhatti_qksms_1155` | non_crash | ✅ | Found the residual `EditText text="Joh"` still present beside the selected John contact chip. | [carbon_log.txt](non_crash/moezbhatti_qksms_1155/carbon_log.txt) |
| `Neamar_KISS_1481` | non_crash | ✅ | Configured all four interdependent settings, added a favourite, then confirmed the favourites bar did not appear on a home-screen tap. | [carbon_log.txt](non_crash/Neamar_KISS_1481/carbon_log.txt) |

## Why the two failed

Both are environment and prerequisite blockers rather than reasoning or
action failures: one needs a Google account the emulator cannot provide,
the other needs app data that the run could not put in place.

Failure to reproduce does not establish that a bug is fixed. Neither
`getodk_collect_360` nor `MarcusWolschon_osmeditor4android_637` was shown
to be fixed upstream; each reason above says only what blocked that run.

[`README.md`](README.md) is the original head-to-head write-up for this
set, case by case against the limitation ReBL's paper states, with the
paper quotes. It predates this document and is kept as written; the
counts and verdicts above are the record.
