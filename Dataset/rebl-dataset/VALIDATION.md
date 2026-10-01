# Validation audit — 2026-09-20

> **Re-verified September 26, 2026:** all 96 APK files match their recorded source binaries, and all 95 available reports match freshly retrieved sources. This does not establish runtime reproduction. The deeper review flags **16 version discrepancies**, alongside the documented alternative, instrumented and archived cases; CarReport#43 still lacks its report.
>
> See the [complete re-verification and per-case setup notes](reverification/2026-09-26/REVERIFICATION.md), [machine-readable readiness manifest](reverification/2026-09-26/case-readiness.json), and [CARBON command helper](reverification/2026-09-26/carbon_case_commands.py). The helper validates selected APK/report hashes and prints explicit commands; it performs no device operation or model call. The published root `run.sh` hardcodes Memento#169 rather than honoring the report argument shown in the root README.

## Scope and result

The original branch was read at `bc03dcd43f11e39f8ed16e56b4babbeb762fcb4a`.
This audit covers only `Dataset/rebl-dataset/`. It compares the complete 96-row ReBL
README index against local files and independently retrieved upstream issue/APK
mapping evidence. All 96 APKs passed ZIP CRC, Android manifest/package, DEX presence,
SHA-256 and source-object checks where applicable. The offline validator checks all
96 cases and fails on undeclared missing files, mismatches, wrong packages, or altered
report snapshots. Its normal success is a **static artifact-integrity result**.

**No emulator/device execution was performed.** Android installation, service access,
setup feasibility, and actual bug reproduction remain unverified for every case.
The strict `--require-complete` gate therefore deliberately fails. No CARBON or ReBL
success rate is inferred from this audit.

## Corrections and recoveries

1. **APKs absent from Git:** the old README claimed 80 included binaries, but the
   repository excluded `*.apk`. Added a folder-local ignore exception and all 96 APKs.
2. **Aegis#415 was Firefox Focus:** old AndroR2+ `apks/275.apk` declares
   `org.mozilla.focus`, version `5.2`. Original AndroR2 metadata identifies ID 275 as
   Focus#2730 and ID **274** as Aegis#415. Replaced it with AndroR2 `274.apk`, package
   `com.beemdevelopment.aegis`, version `1.1.4`, with the issue-specific table/commit.
   The rejected artifact's hash and URL are preserved in the case metadata.
3. **Seven missed issue-specific APKs:** recovered ActivityDiary#285, APhotoMgr#116,
   Anki#5638, Commons#2123, FirefoxLite#5085, ODK#3222 and Osmeditor#637 from Themis.
   Verified its issue table, exact Git blob, package, version and archive integrity.
   Themis documents coverage instrumentation; those APKs are labeled accordingly.
4. **ODK#360:** recovered ReproBot's `yakusu-35.apk`, package `org.odk.collect.android`,
   version `v1.4.13`, matched through its `subjects.csv` issue URL.
5. **Three report-version alternatives:** AndrOBD#144 = F-Droid V2.0.7; Markor#1698 =
   F-Droid 2.8.6; ODK#1796 = official ODK v1.12.2. The first two APK SHA-256 values
   also match F-Droid's archive index. These are explicitly not certified as ReBL's
   original binaries. Markor's previous `8.5a.75.75` hint was incorrect.
6. **ScreenCam#32:** ReCDroid's original ID 36, like ODK's ID 37, is a Memento binary.
   Neither wrong-app file is packaged for those labels. ScreenCam 1.8.2 is supplied
   as a **candidate**: its `VideoRecyclerAdapter.java` is byte-identical to the parent
   of the issue-linked fix `7ef08c83317e8329a84d53bd145d0e6246b9bac9`. The source file
   hash and fix URL are recorded. This is source evidence, not a runtime confirmation.
7. **Report audit:** all 76 originally included GitHub reports match independently
   fetched title/body/all comments after newline normalization. Twelve additional
   GitHub reports were recovered for previously excluded cases. Pagination counts
   were checked against each issue's declared count; pull requests were rejected.
8. **F-Droid comments recovered:** REST notes returned 401, but public GraphQL returned
   all 12 non-system notes (14 including system events), with `hasNextPage=false`.
   Replaced the incomplete report with verified title, description and all 12 comments.
9. **Three deleted live reports recovered:** PdfViewer#33 and Transistor#63 from
   timestamped Wayback captures; Transistor#149 from AndroR2's saved issue HTML.
   Extracted real `.js-comment-body` elements, excluding the composer preview.
   Historical thread completeness is marked unverified rather than assumed.
10. **Metadata/downloader fixes:** resolve binary-manifest version resources; retain
    upstream version disagreements; use immutable Git URLs and recorded hashes;
    reject same-size corruption and wrong package IDs; preserve metadata on skip,
    `--apk-only` and `--br-only`; reject unknown labels; restore reports from reviewed
    snapshots; never silently substitute HTML or truncate a failed comment request.

## Remaining limitation: CarReport#43

The issue-specific ReCDroid APK is present (`me.kuehle.carreport`, version `2.7`).
The original report has not been recovered. The live Bitbucket page returned 401;
its API returned 410 with a deprecation message. Wayback queries for the issue path
and full slug returned no captures. The old claim "no archive anywhere — unrecoverable"
was unjustified and has been removed. No fabricated `bug_report.txt` is supplied.
This remains one unavailable input, not a proven reproduction failure.

## Reproducibility and interpretation

- Raw source snapshots preserve Markdown text and source comment IDs where available.
  `bug_report.txt` uses LF newlines, strips outer whitespace of each section, and
  retains internal whitespace. It is a rendered source snapshot, not byte-identical
  Markdown exported by ReBL. The original K9 example is saved for comparison.
- Three archived reports remain archival even if all visible saved comments were
  extracted. Google Code JSON is the original archive representation, distinct from
  scraped GitHub HTML with potentially collapsed comments.
- Current comments can reveal subsequent fixes and differ from inputs available to
  the 2024 study. Exact study-time report text and summarized `*` inputs are not
  established by matching app names and issue numbers.
- App version strings are not sufficient identity evidence: a debug/rebuilt APK can
  preserve an old versionName. Exact hashes, source commits and source mappings are
  retained. Version disagreements below require review and runtime testing.
- Shared APKs are explicit, not accidental duplicate cases. Every issue still has its
  own report and folder. There are 96 APK paths but 86 distinct binary hashes.
- `expected_crash.txt` and `upstream_setup.py` are from ReproBot's issue-matched
  auxiliary material. They have not been executed or validated against every chosen
  binary; do not feed the oracle to the reproduction model as extra bug-report text.

## Version differences

The prior manifest differs from binary versionName for 22 cases. Current source
mapping tables differ for 27 cases, including legitimate debug/build
suffixes and apparent upstream metadata errors. Neither count establishes that the
binary is fixed or buggy. Exact table versions and actual manifest values follow.

| ReBL label | Prior recorded version | Current source-table version | Actual APK version |
|---|---|---|---|
| ActivityDiary#285 | — | 1.4.0 | 1.4.0-debug |
| AndOPT#500 | 0.7.0 | 0.7.0 | 0.7.0-dev |
| AndOPT#569 | 0.70 | 0.70 | 0.7.1.1 |
| AnglersLog#9 | 1.2.3 | 1.2.3 | 1.2.0 |
| Anki#6432* | 2.12 | 2.12 | 2.12alpha2 |
| AntennaPod#3245 | 1.7.2 | 1.7.2 | 1.7.2b |
| APhotoMgr#116 | — | 0.6.4 | 0.6.4.180314 |
| Commons#2123 | — | 2.9.0 | 2.9.0-debug-buggy-#2123~3a81e3acc |
| FamilyFinance#1 | 1.5.4 | 1.5.4 | 1.5.5-DEBUG |
| FastAdapter#113 | 1.4.1.1 | — | 1.4.1 |
| Field#Book#145 | 4.3.3 | 4.3.3 | 4.3.1 |
| FirefoxLite#5085 | — | 2.1.20 | 2.1.20.debug.ting |
| NewsBlur#1053 | 6.10 | — | 6.1.0 |
| ODK#3222 | — | 1.23.0 | v1.23.0-beta.2-dirty |
| Osmeditor#637* | — | 0.9.10 | 0.9.10.0.1324 |
| Soen#36 | 1.0 | 1.0 | 2.7.268-alpha-2021-04-11 |
| Trainer#7 | 0119 | 0119 | 1.0 |
| Transistor#149 | — | 2.3.3 | 2.3.1 (Kooks) |
| Transistor#63 | — | 1.2.3 | 1.2.3 (Cygnet Committee) |
| Trickytripper#42 | 1.5.8 | 1.5.8 | 1.6.0 |
| (NC)Aegis#415 | 1.14 | — | 1.1.4 |
| (NC)andOPT#638 | 0.8.0 | 0.8.0 | 0.8.0-beta1 |
| (NC)AndOTP#567 | 0.7.1.1 | 0.7.1.1 | 0.7.1.1-dev |
| (NC)AnglesLog#151 | 1.3.3 | 1.3.3 | 1.2.5 |
| (NC)Images2PDF#154 | 2.5.1 | 2.5.1 | 2.5 |
| (NC)K9#3971 | 5.600 | 5.600 | 5.700 |
| (NC)LrkFM#34 * | 2.1.1 | 2.1.1 | 2.0.2 |
| (NC)Markor#1020 | 2.3.2 | 2.3.2 | 2.3.1 |
| (NC)Markor#331 | 1.1.0 | 1.1.0 | 1.0.2 |
| (NC)WiFiAnalyzer#222 | 1.9.3 | 1.9.3 | 2.0.3 |

## Verification commands

```bash
python3 validate_rebl_dataset.py
python3 -m unittest test_dataset_validation.py -v
python3 download_rebl_dataset.py --apk-only
python3 validate_rebl_dataset.py --require-complete
```

The last command is an intentional negative check and must not pass until its stated
completeness and runtime conditions are met. The regression suite exercises wrong
packages, same-size corruption, fake PK headers, metadata preservation, source-index
parsing, missing reports, archive preview exclusion, and recovered GitLab comments.
The full validator also cross-checks source mapping rows and every report rendering.

## Cryptographic signature verification

Ran the official Android SDK Build Tools 35 `apksigner` against every packaged APK.
The default verification succeeded for 78 and failed for 18 because their manifests
advertise API levels below 18 while their JAR signatures use SHA-256/RSA. The failures
are preserved verbatim in `signature_report.json`; they are not hidden or described as
unconditional passes. Rechecking **all 96** with minimum API `max(manifestMinSdk,18)`
and maximum API 35 succeeded. Per-case metadata records the tested API interval and
warnings. This verifies signature integrity for those platform levels; it does not
prove installability, trust in the original signer, or successful bug reproduction.

The tool archive URL and SHA-256 of the apksigner JAR are recorded. The local audit
used a temporary Java 17 runtime, without changing or re-signing any APK. Repeat with
`verify_apk_signatures.py --apksigner PATH_TO_ANDROID_SDK_APKSIGNER`.
