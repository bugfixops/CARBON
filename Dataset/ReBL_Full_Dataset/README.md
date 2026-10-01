# ReBL_Full_Dataset — CARBON on the full ReBL dataset

The complete ReBL-dataset campaign: **95 Android bug reports executed by CARBON on
`gemini-2.5-pro`**, with each case's inputs and its run output stored together in one folder.

| | |
|---|---|
| Executed cases | **95** — 72 under `crash/`, 23 under `non_crash/` |
| Result | **90/95 reproduced (94.7%)** — 20 conversions, 5 not reproduced |
| Model | `gemini-2.5-pro` |
| Dates | 2026-09-26 to 2026-09-28 |
| Input cases on file | 96 (the 95 above plus one never executed, in `untested/`) |
| APKs shipped in-repo | 97 — 96 case APKs plus one patched retest build in `retest_apks/` |

Full per-case breakdown: [`RETEST_SUMMARY.md`](RETEST_SUMMARY.md).

This is a **different dataset and a separate campaign** from the 100-bug gesture-diverse
benchmark in [`../category-testing-gemini-2.5-pro/`](../category-testing-gemini-2.5-pro/). The two
numbers are not comparable and must not be conflated.

## The 90/95 result

The tally is derived from the committed evidence in this directory, not from a reported
figure: 95 executed cases minus the 5 remaining `NOT_REPRODUCIBLE.md` files = 90 reproduced.

**One of the 90 is an ANR, not the reported crash.** `crash/hidroh_materialistic_1067`
triggered a genuine "Materialistic isn't responding" ANR dialog, confirming the reported
timing race, but logcat contains **no FATAL EXCEPTION** for that run. The originally
reported crash signature remains unconfirmed. It is counted as reproduced on the basis of
the on-screen ANR; see
[`crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md`](crash/hidroh_materialistic_1067/REPRODUCED-AS-ANR.md).

The five cases not reproduced:

| Case | Short reason |
|---|---|
| `crash/getodk_collect_360` | Requires Google OAuth sign-in; the emulator cannot complete it. No retest attempted. |
| `crash/ankidroid_Anki-Android_6432` | Two retests (45 min, 1 h) timed out during the ~15-step setup before reaching the trigger. |
| `crash/MarcusWolschon_osmeditor4android_637` | The agent claimed success; the verdict was rejected because logcat shows no crash signature. |
| `non_crash/beemdevelopment_Aegis_287` | Genuine no-repro, confirmed by two independent runs. |
| `non_crash/moezbhatti_qksms_1124` | The in-app preference the report targets is hidden on Android 8+; a literal repro needs API ≤ 25. |

**Failure to reproduce does not establish that a bug is fixed.** Each of the five keeps its
own `NOT_REPRODUCIBLE.md` with the full evidence and caveats, and those files are the
authority — the table above only summarises them.

## Layout

```
ReBL_Full_Dataset/
  crash/<case>/           72 executed cases whose report describes a crash
  non_crash/<case>/       23 executed cases whose report describes non-crash misbehaviour
  untested/<case>/        1 input case that was never executed
  retest_apks/<case>/     patched APK built for a retest (getodk_collect_2525)
  _batch_summaries/       10 per-shard JSON summaries from the 10-way sharded wave
  LOG_FILENAME_MAP.tsv    maps each run log's new path to its original timestamped filename
  RETEST_SUMMARY.md       per-case results, conversions, and the remaining five
  DATASET_PROVENANCE.md   the dataset's own audit/provenance document (96-row index)
  VALIDATION.md           validation audit
  SHA256SUMS              530 recorded digests
  manifest.json  signature_report.json  validation_report.json  fetch_report.json
  download_rebl_dataset.py  validate_rebl_dataset.py  verify_apk_signatures.py
  test_dataset_validation.py  requirements-validation.txt
  sources/                20 archived upstream mapping-evidence files
  reverification/         18 files from the 2026-09-26 re-verification
```

### Per-case files

| File | Present in | What it is |
|---|---|---|
| `<name>.apk` | 96 cases | The pinned APK the case was run against |
| `meta.json` | 96 cases | Case metadata: issue URL, APK provenance, versions, signature checks |
| `bug_report.txt` | 95 cases | The upstream report text given to the agent |
| `source_report.json` | 95 cases | Machine-readable record of where that report came from |
| `expected_crash.txt` | 58 cases | The crash signature the report describes |
| `upstream_setup.py` | 58 cases | Pre-run setup the case needs |
| `carbon_log.txt` | 95 cases | The CARBON run log (one per executed case) |
| `NOT_REPRODUCIBLE.md` | 5 cases | Evidence and reasoning for a non-reproduction |
| `REPRODUCED-AS-ANR.md` | 1 case | The ANR caveat for `hidroh_materialistic_1067` |

`crash/ankidroid_Anki-Android_6432` additionally keeps an earlier run at
`logs/20260926_220929_344.log`; it was retested, and both runs are preserved.

### `untested/`

`untested/frigus02_car-report_43/` holds one input case that was **never executed** and is
excluded from the 95: its upstream report was never recovered, so there were no
reproduction steps to give the agent. See its
[`NOT_RUN.md`](untested/frigus02_car-report_43/NOT_RUN.md) and `UNAVAILABLE.md`.
96 input cases − 95 executed = this one.

## Provenance of the inputs

The inputs were audited before the campaign ran. The record is kept here unmodified:

- [`VALIDATION.md`](VALIDATION.md) — the validation audit, including the 2026-09-26
  re-verification note and the version discrepancies it flags.
- [`DATASET_PROVENANCE.md`](DATASET_PROVENANCE.md) — the dataset's own provenance document
  with the full 96-row index.
- [`SHA256SUMS`](SHA256SUMS) — 530 recorded digests. **528 re-verify; 2 expected failures, see
  below.**
- [`verify_apk_signatures.py`](verify_apk_signatures.py) — APK signature verification;
  results in [`signature_report.json`](signature_report.json).
- [`validate_rebl_dataset.py`](validate_rebl_dataset.py) — dataset validator; results in
  [`validation_report.json`](validation_report.json).
- [`reverification/`](reverification/) and [`sources/`](sources/) — the re-verification
  outputs and the archived upstream mapping evidence.

Note the audit's own caveat: matching APKs and reports establish provenance, **not** runtime
reproduction.

### Running the checksum verification — 2 failures are expected

`shasum -a 256 -c SHA256SUMS` reports **2 failures**, on `DATASET_PROVENANCE.md` (recorded
under its former name `README.md`) and on `VALIDATION.md`. **This is expected and
pre-existing — the artifact is not corrupt.**

- **528 of the 530 entries verify clean:** all 519 case files, and 9 of the 11 top-level
  entries.
- The 2 failures are the dataset's own **prose documents**, not data. Both were edited after
  `SHA256SUMS` was generated: each carries a "Re-verified September 26, 2026" note added on
  top of an audit dated 2026-09-20, so the recorded digests predate the text they cover.
- The staleness is **inherited, not introduced by the restructure.** Extracting the source
  branch's own `SHA256SUMS` together with its own copies of those two files and running
  `shasum -c` there fails the same 2 entries, and both files' git blob hashes are unchanged
  before and after the move.
- `SHA256SUMS` was deliberately **not** rewritten. It is the audited record; correcting it
  here would replace evidence with a reconstruction.

Note also that the recorded paths are relative to the pre-merge flat layout, so entries must
be resolved through the `crash/`, `non_crash/` and `untested/` prefixes — see "Layout changes
made during the merge" below for the one-liner that does this.

## How this set was merged

This campaign was developed on two feature branches and merged into `main` locally.

`origin/rebl-carbon-retest-2` (`cbc11be`) was merged as the authoritative tip.
`origin/rebl-carbon-test` (`ff8a5aa`) was **deliberately not merged**: the two branches share
their first 14 commits and diverge only at the tip, where `cbc11be` is a strict superset. The
divergence covers exactly three bugs — `MarcusWolschon_osmeditor4android_637`,
`beemdevelopment_Aegis_287` and `moezbhatti_qksms_1124` — and for all three `cbc11be` carries
the newer wave-2 logs and the reviewed, more conservative `NOT_REPRODUCIBLE.md` verdicts.
Merging `ff8a5aa` as well would have reintroduced the less-conservative claims. Its history
remains intact on the remote.

The merge's only conflict was `.github/workflows/rebl-carbon-gemini.yml`, where `main` had
added the `apk_url` / `agent_hint` / `pre_setup` retest inputs and `retest-2` had added
`max_repeat` with its `REBL_MAX_REPEAT` env wiring. The `main`→`retest-2` delta on that file
is purely additive, so `retest-2`'s version is the exact union and was taken whole: 14
dispatch inputs, jobs `validate` / `setup` / `retest` / `collect`.

**Known and deliberately unchanged:** that workflow's checkout steps and its `collect` job
still reference the `rebl-carbon-test` branch, which is now historical. Retargeting would
change CI behaviour, so it was left alone and is flagged here instead.

## Relationship to `ReBL_Failed_Dataset/`

[`../ReBL_Failed_Dataset/`](../ReBL_Failed_Dataset/) is a curated **9-bug subset of these
95**, kept separately and unchanged because it is the artifact the paper cites. The
duplication is intentional — do not deduplicate it.

| In `ReBL_Failed_Dataset/` | Here |
|---|---|
| `crash/alexstyl_Memento-Calendar_169` | `crash/alexstyl_Memento-Calendar_169` |
| `crash/ankidroid_Anki-Android_6432` | `crash/ankidroid_Anki-Android_6432` |
| `crash/getodk_collect_360` | `crash/getodk_collect_360` |
| `crash/MarcusWolschon_osmeditor4android_637` | `crash/MarcusWolschon_osmeditor4android_637` |
| `non_crash/cohenadair_anglers-log_347` | `non_crash/cohenadair_anglers-log_347` |
| `non_crash/lfuelling_lrkFM_34` | `non_crash/lfuelling_lrkFM_34` |
| `non_crash/moezbhatti_qksms_1155` | `non_crash/moezbhatti_qksms_1155` |
| `non_crash/Neamar_KISS_1481` | `non_crash/Neamar_KISS_1481` |
| `non_crash/PhenoApps_Field-Book_137` | `non_crash/PhenoApps_Field-Book_137` |

## Layout changes made during the merge

Three things moved, and all three are recorded rather than papered over.

**1. Case files are one directory level deeper, and the provenance files were not rewritten.**
Before the merge, inputs sat flat at `Dataset/rebl-dataset/<case>/` and outputs at
`results/rebl-dataset/{crash,non-crash}/<case>/`. They are now unified under
`crash/`, `non_crash/` and `untested/` (the branch's hyphenated `non-crash` was normalised to
`non_crash` to match `ReBL_Failed_Dataset`). `SHA256SUMS`, `manifest.json`,
`signature_report.json`, `validation_report.json` and `fetch_report.json` are carried over
**byte-identical**, so their recorded paths are relative to the old flat layout. Rewriting them
would have destroyed the audited record, so they were left alone. **528 of the 530 recorded
digests re-verify** by resolving each entry through the three prefixes — every one of the 519
case files, plus 9 of the 11 top-level entries:

```bash
cd Dataset/ReBL_Full_Dataset
while IFS= read -r line; do
  d=${line%%  *}; p=${line#*  }
  [ "$p" = "README.md" ] && p="DATASET_PROVENANCE.md"
  for pre in "" crash/ non_crash/ untested/; do
    [ -f "$pre$p" ] && { printf '%s  %s\n' "$d" "$pre$p"; break; }
  done
done < SHA256SUMS | shasum -a 256 -c
```

The 2 entries that do **not** match are `DATASET_PROVENANCE.md` (recorded as `README.md`) and
`VALIDATION.md`. That is a pre-existing discrepancy in the dataset's own audit record, not
something the move introduced: both documents were edited after `SHA256SUMS` was generated —
each carries a "Re-verified September 26, 2026" note added on top of a 2026-09-20 audit — so
their recorded digests were already stale. Verified by extracting the source branch's own
`SHA256SUMS` and its own copies of those two files and running `shasum -c` there: the same 2
entries fail, and both files' git blob hashes are identical before and after the move. See
"Running the checksum verification" above.

Because of this path shift, `validate_rebl_dataset.py` and `test_dataset_validation.py` assume
the old flat layout and will **not** pass unmodified against this tree. They are kept as the
record of what was run at audit time.

**2. The checksummed `README.md` is now `DATASET_PROVENANCE.md`.** The dataset's original
`README.md` was a 37,520-byte provenance document and is itself a `SHA256SUMS` entry. It was
renamed to `DATASET_PROVENANCE.md` (content unchanged) so this campaign README could take the
`README.md` slot. The `README.md` line in `SHA256SUMS` refers to that document — the one-liner
above applies the alias.

**3. Run logs were renamed to `carbon_log.txt`.** Each case's log was originally
`<YYYYMMDD_HHMMSS_mmm>.log`. The evidence files cite those original filenames, and they were
carried over verbatim rather than edited, so [`LOG_FILENAME_MAP.tsv`](LOG_FILENAME_MAP.tsv)
maps every new path back to its original filename.
