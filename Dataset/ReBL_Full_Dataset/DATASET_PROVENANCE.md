# ReBL dataset for CARBON — audited reconstruction

> **Re-verified September 26, 2026:** all 96 APK files match their recorded source binaries, and all 95 available reports match freshly retrieved sources. This does not establish runtime reproduction. The deeper review flags **16 version discrepancies**, alongside the documented alternative, instrumented and archived cases; CarReport#43 still lacks its report.
>
> See the [complete re-verification and per-case setup notes](reverification/2026-09-26/REVERIFICATION.md), [machine-readable readiness manifest](reverification/2026-09-26/case-readiness.json), and [CARBON command helper](reverification/2026-09-26/carbon_case_commands.py). The helper validates selected APK/report hashes and prints explicit commands; it performs no device operation or model call. The published root `run.sh` hardcodes Memento#169 rather than honoring the report argument shown in the root README.

**96 ReBL labels, 96 APK files, 95 recovered reports. One original report remains unavailable.**
This folder reconstructs the app/issue list in [ReBL's README](https://github.com/datareviewtest/ReBL)
at commit `8c9ce57ff445261a0c40cecb7bb0fb7c17ea2b13` (73 crash + 23 non-crash). It is **not a claim that all 96 bugs
have been reproduced, or that every binary/report equals ReBL's original experimental input**.

The previous folder had no committed APKs, only 80 report/metadata folders, and an
incorrect Aegis APK mapping. This revision includes the binaries, preserves all 96
labels, corrects that mapping, and records source evidence, actual package/version,
and SHA-256 checksums. See [VALIDATION.md](VALIDATION.md) for findings and limitations.

| Artifact/property | Count |
|---|---:|
| ReBL cases (crash / non-crash) | 96 (73 / 23) |
| APKs physically included | 96 (576,451,124 bytes; 86 distinct SHA-256 values) |
| APKs explicitly mapped to this issue by a source benchmark | 92 |
| Alternative APKs matching the issue's stated version | 3 |
| APK candidate supported by pre-fix source code | 1 |
| Complete report snapshots | 92 (88 GitHub, 3 Google Code, 1 GitLab) |
| Archived report snapshots, historical thread completeness unverified | 3 |
| Original report unavailable | 1 (`CarReport#43`) |
| Runtime reproductions performed in this audit | 0 |

## Files and reproduction

Every case has its own `<owner>_<repo>_<issue>/` folder containing:

- `<repo>_<issue>.apk`: actual binary, never an HTML response or Git LFS pointer.
- `bug_report.txt`: title, issue body, and comments in ReBL-style sections (95 cases).
- `source_report.json`: source text and retrieval provenance, used to regenerate the report.
- `meta.json`: same record as the entry in `manifest.json`; package ID, versionCode,
  resolved versionName, Android/ABI information, hashes, pairing qualification and warnings.
- `expected_crash.txt` / `upstream_setup.py`, where supplied by ReproBot: separate
  evaluation/setup material, **not part of the model's bug-report input**. These scripts
  have not been executed in this audit; review paths, device IDs, accounts and data first.

`CarReport#43` has an APK, metadata, and `UNAVAILABLE.md`, without invented report text.
`sources/` holds the pinned ReBL index, source mapping tables, archived issue HTML,
and special-case evidence. `SHA256SUMS` locks the packaged files. `validation_report.json`
records static checks, and `fetch_report.json` records the most recent downloader run's
explicit scope. A limited run is never a certificate for the whole dataset.

`manifest.json` retains `included` (95 APK/report pairs) and `excluded` (the one case
with no report) for compatibility. **Included does not mean runtime validated.** All
96 are part of the benchmark index and all have APKs. Use `apk_pairing`, `report_status`,
`validation_warnings`, and `runtime_status` to select an explicitly disclosed evaluation subset.

```bash
cd Dataset/rebl-dataset
python3 -m venv .venv
.venv/bin/pip install -r requirements-validation.txt

# Offline validation of every APK, report, metadata record and index mapping.
.venv/bin/python validate_rebl_dataset.py
.venv/bin/python -m unittest test_dataset_validation.py -v

# Restore a missing/damaged APK from its pinned URL. Existing files are HASH checked.
.venv/bin/python download_rebl_dataset.py --apk-only
.venv/bin/python download_rebl_dataset.py --only 'K9#3255'

# Inventory without downloading; exact labels are required (quote # and *).
.venv/bin/python download_rebl_dataset.py --dry-run

# Intentionally fails until EVERY case has sufficient provenance and runtime evidence.
.venv/bin/python validate_rebl_dataset.py --require-complete
```

The downloader needs Python, `curl`, and the validation dependencies. It restores
reports from the audited source snapshots rather than silently replacing benchmark
input with newer live comments. `--out DIR`, `--limit N`, `--only LABEL`, `--force`,
`--apk-only` and `--br-only` are supported. `--apk-only` and `--br-only` are mutually
exclusive. SHA checks cannot be disabled. The default all-artifact run reports a failure
for CarReport's unavailable report; the other 95 pairs are still processed. A successful
fetch means the requested files match the audit, not that a bug reproduces.

## Run a selected case with CARBON

Use an Android device/emulator compatible with the case's `android_os`, `min_sdk`,
`target_sdk`, and native ABIs. Do not assume one modern emulator can run this entire
historical dataset. Start from a clean emulator snapshot or clean application state
between cases; multiple issues share packages and some APKs have different signing keys.
Install the selected APK, launch the exact `apk_package` / `main_activity` in its
`meta.json`, and prepare any accounts, data files, network service or permissions
required by the report and setup material. Installation, launch, required setup and
bug reproduction all still need device verification.

For example, from the repository's `Automation/` directory after installing and
opening the K9 APK:

```bash
python3 reproduction.py 5554 ../Dataset/rebl-dataset/thunderbird_thunderbird-android_3255/bug_report.txt
```

`5554` is the emulator port, matching `emulator-5554`. Configure CARBON's normal
model and environment prerequisites first. Capture logcat, screenshots/video, the
input hash, APK hash, device configuration and a manually checked bug oracle.
Do not count an installation error, missing service, or unverified candidate as a
successful or failed bug reproduction without separately recording that limitation.

## Interpretation for a CARBON/ReBL comparison

- This is a **reconstruction of the README's cases**. The public ReBL repository ships
  only one example report and no APK set. Its README alone cannot prove binary identity.
- Themis's seven recovered APKs are instrumented builds. Three additional releases
  are version-matched alternatives, and ScreenCam#32 is a source-supported candidate.
  Report results for these groups separately, or disclose the exact evaluated subset.
- APK manifest versions override old filename/table guesses. The original recorded
  versions and table disagreements remain visible in metadata and the audit report.
  A source benchmark's issue mapping does not prove that a particular bug still reproduces.
- Live reports were captured on **2026-09-20**, including comments posted after the
  ReBL paper. These comments can contain fixes, hints, or changed behavior. They are
  not certified as ReBL's historical inputs. Archive dates are recorded separately.
- ReBL's `*` means summarization was applied. The public package does not supply those
  exact summarized inputs; this folder keeps the source report and the `*` marker.
- Keep the denominator visible: 96 indexed, 95 reports available; never present a
  smaller tested subset as a complete 96-case benchmark without explaining omissions.

## APK signature and Android compatibility

All 96 APKs passed Android SDK Build Tools 35 `apksigner` verification for API
`max(manifestMinSdk, 18)` through 35. The command output and signer certificates are
recorded in `signature_report.json`. **18 APKs fail the tool's default check across
all declared API levels** because their SHA-256/RSA signatures are not supported on
API 17 or below. Their metadata records this minimum-API restriction. No APK was
modified or re-signed. Signature validity does not prove installation or runtime
compatibility on a given device. Behavior beyond API 35 was not verified.

To independently repeat cryptographic verification with your Android SDK:

```bash
python3 verify_apk_signatures.py --apksigner "$ANDROID_SDK_ROOT/build-tools/35.0.0/apksigner"
```

The normal offline validator checks hashes against the recorded signature results;
it does not rerun `apksigner`. Use the command above to perform that verification again.

## All 96 cases

Pairing: **benchmark** = issue-pinned source benchmark; **version match** = release
matching the issue's stated version; **candidate** = pre-fix source evidence, runtime
confirmation required. Report: **complete**, **archived**, or **unavailable**.
Actual version comes from the APK; `—` means no versionName was declared.

| # | ReBL label | Actual package | APK version | Pairing | Report | Files |
|---:|---|---|---|---|---|---|
| 1 | [ActivityDiary#285](https://github.com/ramack/ActivityDiary/issues/285) | `de.rampro.activitydiary.debug` | 1.4.0-debug | benchmark | [complete](ramack_ActivityDiary_285/bug_report.txt) | [APK](ramack_ActivityDiary_285/ActivityDiary_285.apk) · [metadata](ramack_ActivityDiary_285/meta.json) |
| 2 | [Acv#12](https://github.com/robotmedia/droid-comic-viewer/issues/12) | `net.androidcomics.acv` | 1.4.1.4 | benchmark | [complete](robotmedia_droid-comic-viewer_12/bug_report.txt) | [APK](robotmedia_droid-comic-viewer_12/droid-comic-viewer_12.apk) · [metadata](robotmedia_droid-comic-viewer_12/meta.json) |
| 3 | [Aegis#500](https://github.com/beemdevelopment/Aegis/issues/500) | `com.beemdevelopment.aegis` | 1.2 | benchmark | [complete](beemdevelopment_Aegis_500/bug_report.txt) | [APK](beemdevelopment_Aegis_500/Aegis_500.apk) · [metadata](beemdevelopment_Aegis_500/meta.json) |
| 4 | [Aimsicd#816*](https://github.com/CellularPrivacy/Android-IMSI-Catcher-Detector/issues/816) | `com.SecUpwN.AIMSICD` | unspecified-normal | benchmark | [complete](CellularPrivacy_Android-IMSI-Catcher-Detector_816/bug_report.txt) | [APK](CellularPrivacy_Android-IMSI-Catcher-Detector_816/Android-IMSI-Catcher-Detector_816.apk) · [metadata](CellularPrivacy_Android-IMSI-Catcher-Detector_816/meta.json) |
| 5 | [AndOPT#135](https://github.com/andOTP/andOTP/issues/135) | `org.shadowice.flocke.andotp` | 0.4.0.1 | benchmark | [complete](andOTP_andOTP_135/bug_report.txt) | [APK](andOTP_andOTP_135/andOTP_135.apk) · [metadata](andOTP_andOTP_135/meta.json) |
| 6 | [AndOPT#500](https://github.com/andOTP/andOTP/issues/500) | `org.shadowice.flocke.andotp.dev` | 0.7.0-dev | benchmark | [complete](andOTP_andOTP_500/bug_report.txt) | [APK](andOTP_andOTP_500/andOTP_500.apk) · [metadata](andOTP_andOTP_500/meta.json) |
| 7 | [AndOPT#569](https://github.com/andOTP/andOTP/issues/569) | `org.shadowice.flocke.andotp` | 0.7.1.1 | benchmark | [complete](andOTP_andOTP_569/bug_report.txt) | [APK](andOTP_andOTP_569/andOTP_569.apk) · [metadata](andOTP_andOTP_569/meta.json) |
| 8 | [AnglersLog#9](https://github.com/cohenadair/anglers-log/issues/9) | `com.cohenadair.anglerslog` | 1.2.0 | benchmark | [complete](cohenadair_anglers-log_9/bug_report.txt) | [APK](cohenadair_anglers-log_9/anglers-log_9.apk) · [metadata](cohenadair_anglers-log_9/meta.json) |
| 9 | [Anki#4586](https://github.com/ankidroid/Anki-Android/issues/4586) | `com.ichi2.anki` | 2.9alpha4 | benchmark | [complete](ankidroid_Anki-Android_4586/bug_report.txt) | [APK](ankidroid_Anki-Android_4586/Anki-Android_4586.apk) · [metadata](ankidroid_Anki-Android_4586/meta.json) |
| 10 | [Anki#5638](https://github.com/ankidroid/Anki-Android/issues/5638) | `com.ichi2.anki` | 2.9.1 | benchmark | [complete](ankidroid_Anki-Android_5638/bug_report.txt) | [APK](ankidroid_Anki-Android_5638/Anki-Android_5638.apk) · [metadata](ankidroid_Anki-Android_5638/meta.json) |
| 11 | [Anki#6432*](https://github.com/ankidroid/Anki-Android/issues/6432) | `com.ichi2.anki` | 2.12alpha2 | benchmark | [complete](ankidroid_Anki-Android_6432/bug_report.txt) | [APK](ankidroid_Anki-Android_6432/Anki-Android_6432.apk) · [metadata](ankidroid_Anki-Android_6432/meta.json) |
| 12 | [AntennaPod#3245](https://github.com/AntennaPod/AntennaPod/issues/3245) | `de.danoeh.antennapod.debug` | 1.7.2b | benchmark | [complete](AntennaPod_AntennaPod_3245/bug_report.txt) | [APK](AntennaPod_AntennaPod_3245/AntennaPod_3245.apk) · [metadata](AntennaPod_AntennaPod_3245/meta.json) |
| 13 | [Anymemo#18](https://code.google.com/archive/p/anymemo/issues/18) | `org.liberty.android.fantastischmemo` | 8.999.4 | benchmark | [complete](helloworld1_AnyMemo_18/bug_report.txt) | [APK](helloworld1_AnyMemo_18/AnyMemo_18.apk) · [metadata](helloworld1_AnyMemo_18/meta.json) |
| 14 | [Anymemo#422](https://github.com/helloworld1/AnyMemo/issues/422) | `org.liberty.android.fantastischmemo` | 10.9.992-b191202 | benchmark | [complete](helloworld1_AnyMemo_422/bug_report.txt) | [APK](helloworld1_AnyMemo_422/AnyMemo_422.apk) · [metadata](helloworld1_AnyMemo_422/meta.json) |
| 15 | [Anymemo#440](https://github.com/helloworld1/AnyMemo/issues/440) | `org.liberty.android.fantastischmemo` | 10.10.1 | benchmark | [complete](helloworld1_AnyMemo_440/bug_report.txt) | [APK](helloworld1_AnyMemo_440/AnyMemo_440.apk) · [metadata](helloworld1_AnyMemo_440/meta.json) |
| 16 | [APhotoMgr#116](https://github.com/k3b/APhotoManager/issues/116) | `de.k3b.android.androFotoFinder` | 0.6.4.180314 | benchmark | [complete](k3b_APhotoManager_116/bug_report.txt) | [APK](k3b_APhotoManager_116/APhotoManager_116.apk) · [metadata](k3b_APhotoManager_116/meta.json) |
| 17 | [AsciiCam#17](https://github.com/dozingcat/AsciiCam/issues/17) | `com.dozingcatsoftware.asciicam` | 1.2.3 | benchmark | [complete](dozingcat_AsciiCam_17/bug_report.txt) | [APK](dozingcat_AsciiCam_17/AsciiCam_17.apk) · [metadata](dozingcat_AsciiCam_17/meta.json) |
| 18 | [Birthdroid#13](https://github.com/rigid/Birthdroid/issues/13) | `com.rigid.birthdroid` | 0.6.3 | benchmark | [complete](rigid_Birthdroid_13/bug_report.txt) | [APK](rigid_Birthdroid_13/Birthdroid_13.apk) · [metadata](rigid_Birthdroid_13/meta.json) |
| 19 | [Calendula#134](https://github.com/citiususc/calendula/issues/134) | `es.usc.citius.servando.calendula` | 2.5.7 | benchmark | [complete](citiususc_calendula_134/bug_report.txt) | [APK](citiususc_calendula_134/calendula_134.apk) · [metadata](citiususc_calendula_134/meta.json) |
| 20 | [CarReport#43](https://bitbucket.org/frigus02/car-report/issues/43) | `me.kuehle.carreport` | 2.7 | benchmark | [unavailable](frigus02_car-report_43/UNAVAILABLE.md) | [APK](frigus02_car-report_43/car-report_43.apk) · [metadata](frigus02_car-report_43/meta.json) |
| 21 | [Commons#2123](https://github.com/commons-app/apps-android-commons/issues/2123) | `fr.free.nrw.commons.beta` | 2.9.0-debug-buggy-#2123~3a81e3acc | benchmark | [complete](commons-app_apps-android-commons_2123/bug_report.txt) | [APK](commons-app_apps-android-commons_2123/apps-android-commons_2123.apk) · [metadata](commons-app_apps-android-commons_2123/meta.json) |
| 22 | [Dagger#46](https://github.com/vestrel00/android-dagger-butterknife-mvp/issues/46) | `com.vestrel00.daggerbutterknifemvp` | 1.0.0 | benchmark | [complete](vestrel00_android-dagger-butterknife-mvp_46/bug_report.txt) | [APK](vestrel00_android-dagger-butterknife-mvp_46/android-dagger-butterknife-mvp_46.apk) · [metadata](vestrel00_android-dagger-butterknife-mvp_46/meta.json) |
| 23 | [FamilyFinance#1](https://github.com/zwieback/FamilyFinance/issues/1) | `io.github.zwieback.familyfinance.debug` | 1.5.5-DEBUG | benchmark | [complete](zwieback_FamilyFinance_1/bug_report.txt) | [APK](zwieback_FamilyFinance_1/FamilyFinance_1.apk) · [metadata](zwieback_FamilyFinance_1/meta.json) |
| 24 | [FastAdapter#394](https://github.com/mikepenz/FastAdapter/issues/394) | `com.mikepenz.fastadapter.app` | 2.5.1 | benchmark | [complete](mikepenz_FastAdapter_394/bug_report.txt) | [APK](mikepenz_FastAdapter_394/FastAdapter_394.apk) · [metadata](mikepenz_FastAdapter_394/meta.json) |
| 25 | [FastAdapter#113](https://github.com/mikepenz/FastAdapter/issues/113) | `com.mikepenz.fastadapter.app` | 1.4.1 | benchmark | [complete](mikepenz_FastAdapter_113/bug_report.txt) | [APK](mikepenz_FastAdapter_113/FastAdapter_113.apk) · [metadata](mikepenz_FastAdapter_113/meta.json) |
| 26 | [Fastfitness#142](https://github.com/brodeurlv/fastnfitness/issues/142) | `com.easyfitness` | 0.19.0.1 | benchmark | [complete](brodeurlv_fastnfitness_142/bug_report.txt) | [APK](brodeurlv_fastnfitness_142/fastnfitness_142.apk) · [metadata](brodeurlv_fastnfitness_142/meta.json) |
| 27 | [Fdroid#1821*](https://gitlab.com/fdroid/fdroidclient/-/issues/1821) | `org.fdroid.fdroid` | 1.6.2 | benchmark | [complete](fdroid_fdroidclient_1821/bug_report.txt) | [APK](fdroid_fdroidclient_1821/fdroidclient_1821.apk) · [metadata](fdroid_fdroidclient_1821/meta.json) |
| 28 | [Field#Book#145](https://github.com/PhenoApps/Field-Book/issues/145) | `com.fieldbook.tracker` | 4.3.1 | benchmark | [complete](PhenoApps_Field-Book_145/bug_report.txt) | [APK](PhenoApps_Field-Book_145/Field-Book_145.apk) · [metadata](PhenoApps_Field-Book_145/meta.json) |
| 29 | [Field#Book#146](https://github.com/PhenoApps/Field-Book/issues/146) | `com.fieldbook.tracker` | 4.3.3 | benchmark | [complete](PhenoApps_Field-Book_146/bug_report.txt) | [APK](PhenoApps_Field-Book_146/Field-Book_146.apk) · [metadata](PhenoApps_Field-Book_146/meta.json) |
| 30 | [FirefoxLite#5085](https://github.com/mozilla-mobile/FirefoxLite/issues/5085) | `org.mozilla.rocket.debug.ting` | 2.1.20.debug.ting | benchmark | [complete](mozilla-mobile_FirefoxLite_5085/bug_report.txt) | [APK](mozilla-mobile_FirefoxLite_5085/FirefoxLite_5085.apk) · [metadata](mozilla-mobile_FirefoxLite_5085/meta.json) |
| 31 | [FlashCards#13](https://github.com/ASU-CodeDevils/FlashCards/issues/13) | `com.example.terin.asu_flashcardapp` | 1.0 | benchmark | [complete](ASU-CodeDevils_FlashCards_13/bug_report.txt) | [APK](ASU-CodeDevils_FlashCards_13/FlashCards_13.apk) · [metadata](ASU-CodeDevils_FlashCards_13/meta.json) |
| 32 | [K9#3255](https://github.com/thunderbird/thunderbird-android/issues/3255) | `com.fsck.k9` | 5.403 | benchmark | [complete](thunderbird_thunderbird-android_3255/bug_report.txt) | [APK](thunderbird_thunderbird-android_3255/thunderbird-android_3255.apk) · [metadata](thunderbird_thunderbird-android_3255/meta.json) |
| 33 | [Kiwix#990](https://github.com/kiwix/kiwix-android/issues/990) | `org.kiwix.kiwixmobile` | 2.3 | benchmark | [complete](kiwix_kiwix-android_990/bug_report.txt) | [APK](kiwix_kiwix-android_990/kiwix-android_990.apk) · [metadata](kiwix_kiwix-android_990/meta.json) |
| 34 | [LibreNews#22](https://github.com/milesmcc/LibreNews-Android/issues/22) | `app.librenews.io.librenews` | 1.4 | benchmark | [complete](milesmcc_LibreNews-Android_22/bug_report.txt) | [APK](milesmcc_LibreNews-Android_22/LibreNews-Android_22.apk) · [metadata](milesmcc_LibreNews-Android_22/meta.json) |
| 35 | [LibreNews#23](https://github.com/milesmcc/LibreNews-Android/issues/23) | `app.librenews.io.librenews` | 1.4 | benchmark | [complete](milesmcc_LibreNews-Android_23/bug_report.txt) | [APK](milesmcc_LibreNews-Android_23/LibreNews-Android_23.apk) · [metadata](milesmcc_LibreNews-Android_23/meta.json) |
| 36 | [LibreNews#27](https://github.com/milesmcc/LibreNews-Android/issues/27) | `app.librenews.io.librenews` | 1.4 | benchmark | [complete](milesmcc_LibreNews-Android_27/bug_report.txt) | [APK](milesmcc_LibreNews-Android_27/LibreNews-Android_27.apk) · [metadata](milesmcc_LibreNews-Android_27/meta.json) |
| 37 | [Lrk#44](https://github.com/lfuelling/lrkFM/issues/44) | `io.lerk.lrkFM` | 2.3.0 | benchmark | [complete](lfuelling_lrkFM_44/bug_report.txt) | [APK](lfuelling_lrkFM_44/lrkFM_44.apk) · [metadata](lfuelling_lrkFM_44/meta.json) |
| 38 | [Markor#1698](https://github.com/gsantner/markor/issues/1698) | `net.gsantner.markor` | 2.8.6 | version match | [complete](gsantner_markor_1698/bug_report.txt) | [APK](gsantner_markor_1698/markor_1698.apk) · [metadata](gsantner_markor_1698/meta.json) |
| 39 | [Markor#194](https://github.com/gsantner/markor/issues/194) | `net.gsantner.markor` | 0.3.2 | benchmark | [complete](gsantner_markor_194/bug_report.txt) | [APK](gsantner_markor_194/markor_194.apk) · [metadata](gsantner_markor_194/meta.json) |
| 40 | [Materialistic#1067](https://github.com/hidroh/materialistic/issues/1067) | `io.github.hidroh.materialistic` | 3.2 | benchmark | [complete](hidroh_materialistic_1067/bug_report.txt) | [APK](hidroh_materialistic_1067/materialistic_1067.apk) · [metadata](hidroh_materialistic_1067/meta.json) |
| 41 | [Memento#169*](https://github.com/alexstyl/Memento-Calendar/issues/169) | `com.alexstyl.specialdates` | 3.6 | benchmark | [complete](alexstyl_Memento-Calendar_169/bug_report.txt) | [APK](alexstyl_Memento-Calendar_169/Memento-Calendar_169.apk) · [metadata](alexstyl_Memento-Calendar_169/meta.json) |
| 42 | [MicroMath#39](https://github.com/mkulesh/microMathematics/issues/39) | `com.mkulesh.micromath.plus` | 2.15.4 | benchmark | [complete](mkulesh_microMathematics_39/bug_report.txt) | [APK](mkulesh_microMathematics_39/microMathematics_39.apk) · [metadata](mkulesh_microMathematics_39/meta.json) |
| 43 | [NewsBlur#1053](https://github.com/samuelclay/NewsBlur/issues/1053) | `com.newsblur` | 6.1.0 | benchmark | [complete](samuelclay_NewsBlur_1053/bug_report.txt) | [APK](samuelclay_NewsBlur_1053/NewsBlur_1053.apk) · [metadata](samuelclay_NewsBlur_1053/meta.json) |
| 44 | [NoadPlayer#1](https://github.com/gauravjot/android-noad-music-player/issues/1) | `com.droidheat.musicplayer` | 0.8.20190518-2 | benchmark | [complete](gauravjot_android-noad-music-player_1/bug_report.txt) | [APK](gauravjot_android-noad-music-player_1/android-noad-music-player_1.apk) · [metadata](gauravjot_android-noad-music-player_1/meta.json) |
| 45 | [Notepad#23](https://code.google.com/archive/p/banderlabs/issues/23) | `bander.notepad` | 1.06 | benchmark | [complete](banderlabs_notepad_23/bug_report.txt) | [APK](banderlabs_notepad_23/notepad_23.apk) · [metadata](banderlabs_notepad_23/meta.json) |
| 46 | [Obdreader#22](https://github.com/pires/android-obd-reader/issues/22) | `pt.lighthouselabs.obd.reader` | 2.0 | benchmark | [complete](pires_android-obd-reader_22/bug_report.txt) | [APK](pires_android-obd-reader_22/android-obd-reader_22.apk) · [metadata](pires_android-obd-reader_22/meta.json) |
| 47 | [ODK#360*](https://github.com/getodk/collect/issues/360) | `org.odk.collect.android` | v1.4.13 | benchmark | [complete](getodk_collect_360/bug_report.txt) | [APK](getodk_collect_360/collect_360.apk) · [metadata](getodk_collect_360/meta.json) |
| 48 | [ODK#1402](https://github.com/getodk/collect/issues/1402) | `org.odk.collect.android` | — | benchmark | [complete](getodk_collect_1402/bug_report.txt) | [APK](getodk_collect_1402/collect_1402.apk) · [metadata](getodk_collect_1402/meta.json) |
| 49 | [ODK#1796](https://github.com/getodk/collect/issues/1796) | `org.odk.collect.android` | v1.12.2 | version match | [complete](getodk_collect_1796/bug_report.txt) | [APK](getodk_collect_1796/collect_1796.apk) · [metadata](getodk_collect_1796/meta.json) |
| 50 | [ODK#2075](https://github.com/getodk/collect/issues/2075) | `org.odk.collect.android` | v1.14.0-beta.1 | benchmark | [complete](getodk_collect_2075/bug_report.txt) | [APK](getodk_collect_2075/collect_2075.apk) · [metadata](getodk_collect_2075/meta.json) |
| 51 | [ODK#2086](https://github.com/getodk/collect/issues/2086) | `org.odk.collect.android` | v1.14.0-beta.1 | benchmark | [complete](getodk_collect_2086/bug_report.txt) | [APK](getodk_collect_2086/collect_2086.apk) · [metadata](getodk_collect_2086/meta.json) |
| 52 | [ODK#2191](https://github.com/getodk/collect/issues/2191) | `org.odk.collect.android` | v1.14.0-beta.1 | benchmark | [complete](getodk_collect_2191/bug_report.txt) | [APK](getodk_collect_2191/collect_2191.apk) · [metadata](getodk_collect_2191/meta.json) |
| 53 | [ODK#2525](https://github.com/getodk/collect/issues/2525) | `org.odk.collect.android` | — | benchmark | [complete](getodk_collect_2525/bug_report.txt) | [APK](getodk_collect_2525/collect_2525.apk) · [metadata](getodk_collect_2525/meta.json) |
| 54 | [ODK#3222](https://github.com/getodk/collect/issues/3222) | `org.odk.collect.android` | v1.23.0-beta.2-dirty | benchmark | [complete](getodk_collect_3222/bug_report.txt) | [APK](getodk_collect_3222/collect_3222.apk) · [metadata](getodk_collect_3222/meta.json) |
| 55 | [Olam#1](https://github.com/vishnus/Olam/issues/1) | `com.olam` | 1.0 | benchmark | [complete](vishnus_Olam_1/bug_report.txt) | [APK](vishnus_Olam_1/Olam_1.apk) · [metadata](vishnus_Olam_1/meta.json) |
| 56 | [Olam#2](https://github.com/vishnus/Olam/issues/2) | `com.olam` | 1.0 | benchmark | [complete](vishnus_Olam_2/bug_report.txt) | [APK](vishnus_Olam_2/Olam_2.apk) · [metadata](vishnus_Olam_2/meta.json) |
| 57 | [Sudoku#173](https://code.google.com/archive/p/opensudoku-android/issues/173) | `cz.romario.opensudoku` | 1.1.2 | benchmark | [complete](opensudoku-android_OpenSudoku_173/bug_report.txt) | [APK](opensudoku-android_OpenSudoku_173/OpenSudoku_173.apk) · [metadata](opensudoku-android_OpenSudoku_173/meta.json) |
| 58 | [Osmeditor#637*](https://github.com/MarcusWolschon/osmeditor4android/issues/637) | `de.blau.android` | 0.9.10.0.1324 | benchmark | [complete](MarcusWolschon_osmeditor4android_637/bug_report.txt) | [APK](MarcusWolschon_osmeditor4android_637/osmeditor4android_637.apk) · [metadata](MarcusWolschon_osmeditor4android_637/meta.json) |
| 59 | [PdfViewer#33](https://github.com/JavaCafe01/PdfViewer/issues/33) | `com.gsnathan.pdfviewer` | 3.1 | benchmark | [archived](javacafe01_PdfViewer_33/bug_report.txt) | [APK](javacafe01_PdfViewer_33/PdfViewer_33.apk) · [metadata](javacafe01_PdfViewer_33/meta.json) |
| 60 | [Qksms#482](https://github.com/moezbhatti/qksms/issues/482) | `com.moez.QKSMS` | 2.6.0 | benchmark | [complete](moezbhatti_qksms_482/bug_report.txt) | [APK](moezbhatti_qksms_482/qksms_482.apk) · [metadata](moezbhatti_qksms_482/meta.json) |
| 61 | [Qksms#585](https://github.com/moezbhatti/qksms/issues/585) | `com.moez.QKSMS` | 2.7.1 | benchmark | [complete](moezbhatti_qksms_585/bug_report.txt) | [APK](moezbhatti_qksms_585/qksms_585.apk) · [metadata](moezbhatti_qksms_585/meta.json) |
| 62 | [Screencam#25](https://github.com/vijai1996/screenrecorder/issues/25) | `com.orpheusdroid.screenrecorder` | 1.8.2 | benchmark | [complete](vijai1996_screenrecorder_25/bug_report.txt) | [APK](vijai1996_screenrecorder_25/screenrecorder_25.apk) · [metadata](vijai1996_screenrecorder_25/meta.json) |
| 63 | [Screencam#32](https://github.com/vijai1996/screenrecorder/issues/32) | `com.orpheusdroid.screenrecorder` | 1.8.2 | candidate | [complete](vijai1996_screenrecorder_32/bug_report.txt) | [APK](vijai1996_screenrecorder_32/screenrecorder_32.apk) · [metadata](vijai1996_screenrecorder_32/meta.json) |
| 64 | [Soen#36](https://github.com/alexstojda/soen390/issues/36) | `org.wikipedia.alpha` | 2.7.268-alpha-2021-04-11 | benchmark | [complete](alexstojda_soen390_36/bug_report.txt) | [APK](alexstojda_soen390_36/soen390_36.apk) · [metadata](alexstojda_soen390_36/meta.json) |
| 65 | [Timetracker#10](https://github.com/netmackan/ATimeTracker/issues/10) | `com.markuspage.android.atimetracker` | 0.17 | benchmark | [complete](netmackan_ATimeTracker_10/bug_report.txt) | [APK](netmackan_ATimeTracker_10/ATimeTracker_10.apk) · [metadata](netmackan_ATimeTracker_10/meta.json) |
| 66 | [Timetracker#138](https://github.com/netmackan/ATimeTracker/issues/138) | `com.markuspage.android.atimetracker` | 0.51.2 | benchmark | [complete](netmackan_ATimeTracker_138/bug_report.txt) | [APK](netmackan_ATimeTracker_138/ATimeTracker_138.apk) · [metadata](netmackan_ATimeTracker_138/meta.json) |
| 67 | [Timetracker#35](https://github.com/netmackan/ATimeTracker/issues/35) | `com.markuspage.android.atimetracker` | 0.20 | benchmark | [complete](netmackan_ATimeTracker_35/bug_report.txt) | [APK](netmackan_ATimeTracker_35/ATimeTracker_35.apk) · [metadata](netmackan_ATimeTracker_35/meta.json) |
| 68 | [Trainer#7](https://github.com/moritz-herzog/Trainer-App/issues/7) | `com.german_software_engineers.trainerapp` | 1.0 | benchmark | [complete](moritz-herzog_Trainer-App_7/bug_report.txt) | [APK](moritz-herzog_Trainer-App_7/Trainer-App_7.apk) · [metadata](moritz-herzog_Trainer-App_7/meta.json) |
| 69 | [Transistor#149](https://github.com/y20k/transistor/issues/149) | `org.y20k.transistor` | 2.3.1 (Kooks) | benchmark | [archived](y20k_transistor_149/bug_report.txt) | [APK](y20k_transistor_149/transistor_149.apk) · [metadata](y20k_transistor_149/meta.json) |
| 70 | [Transistor#63](https://github.com/y20k/transistor/issues/63) | `org.y20k.transistor` | 1.2.3 (Cygnet Committee) | benchmark | [archived](y20k_transistor_63/bug_report.txt) | [APK](y20k_transistor_63/transistor_63.apk) · [metadata](y20k_transistor_63/meta.json) |
| 71 | [Trickytripper#42](https://github.com/koelleChristian/trickytripper/issues/42) | `de.koelle.christian.trickytripper` | 1.6.0 | benchmark | [complete](koelleChristian_trickytripper_42/bug_report.txt) | [APK](koelleChristian_trickytripper_42/trickytripper_42.apk) · [metadata](koelleChristian_trickytripper_42/meta.json) |
| 72 | [Ultrasonic#187](https://github.com/ultrasonic/ultrasonic/issues/187) | `org.moire.ultrasonic` | 2.3.1 | benchmark | [complete](ultrasonic_ultrasonic_187/bug_report.txt) | [APK](ultrasonic_ultrasonic_187/ultrasonic_187.apk) · [metadata](ultrasonic_ultrasonic_187/meta.json) |
| 73 | [Weather#61](https://github.com/SecUSo/privacy-friendly-weather/issues/61) | `org.secuso.privacyfriendlyweather` | 2.0 | benchmark | [complete](SecUSo_privacy-friendly-weather_61/bug_report.txt) | [APK](SecUSo_privacy-friendly-weather_61/privacy-friendly-weather_61.apk) · [metadata](SecUSo_privacy-friendly-weather_61/meta.json) |
| 74 | [(NC)Aegis#287](https://github.com/beemdevelopment/Aegis/issues/287) | `com.beemdevelopment.aegis` | 1.1.1 | benchmark | [complete](beemdevelopment_Aegis_287/bug_report.txt) | [APK](beemdevelopment_Aegis_287/Aegis_287.apk) · [metadata](beemdevelopment_Aegis_287/meta.json) |
| 75 | [(NC)Aegis#415](https://github.com/beemdevelopment/Aegis/issues/415) | `com.beemdevelopment.aegis` | 1.1.4 | benchmark | [complete](beemdevelopment_Aegis_415/bug_report.txt) | [APK](beemdevelopment_Aegis_415/Aegis_415.apk) · [metadata](beemdevelopment_Aegis_415/meta.json) |
| 76 | [(NC)Aegis#473](https://github.com/beemdevelopment/Aegis/issues/473) | `com.beemdevelopment.aegis` | 1.2 | benchmark | [complete](beemdevelopment_Aegis_473/bug_report.txt) | [APK](beemdevelopment_Aegis_473/Aegis_473.apk) · [metadata](beemdevelopment_Aegis_473/meta.json) |
| 77 | [(NC)andOPT#580](https://github.com/andOTP/andOTP/issues/580) | `org.shadowice.flocke.andotp` | 0.7.1.1 | benchmark | [complete](andOTP_andOTP_580/bug_report.txt) | [APK](andOTP_andOTP_580/andOTP_580.apk) · [metadata](andOTP_andOTP_580/meta.json) |
| 78 | [(NC)andOPT#638](https://github.com/andOTP/andOTP/issues/638) | `org.shadowice.flocke.andotp` | 0.8.0-beta1 | benchmark | [complete](andOTP_andOTP_638/bug_report.txt) | [APK](andOTP_andOTP_638/andOTP_638.apk) · [metadata](andOTP_andOTP_638/meta.json) |
| 79 | [(NC)AndOTP#567](https://github.com/andOTP/andOTP/issues/567) | `org.shadowice.flocke.andotp.dev` | 0.7.1.1-dev | benchmark | [complete](andOTP_andOTP_567/bug_report.txt) | [APK](andOTP_andOTP_567/andOTP_567.apk) · [metadata](andOTP_andOTP_567/meta.json) |
| 80 | [(NC)AndrOBD#144](https://github.com/fr3ts0n/AndrOBD/issues/144) | `com.fr3ts0n.ecu.gui.androbd` | V2.0.7 | version match | [complete](fr3ts0n_AndrOBD_144/bug_report.txt) | [APK](fr3ts0n_AndrOBD_144/AndrOBD_144.apk) · [metadata](fr3ts0n_AndrOBD_144/meta.json) |
| 81 | [(NC)AnglesLog#151](https://github.com/cohenadair/anglers-log/issues/151) | `com.cohenadair.anglerslog` | 1.2.5 | benchmark | [complete](cohenadair_anglers-log_151/bug_report.txt) | [APK](cohenadair_anglers-log_151/anglers-log_151.apk) · [metadata](cohenadair_anglers-log_151/meta.json) |
| 82 | [(NC)AnglesLog#347*](https://github.com/cohenadair/anglers-log/issues/347) | `com.cohenadair.anglerslog` | 1.3.1 | benchmark | [complete](cohenadair_anglers-log_347/bug_report.txt) | [APK](cohenadair_anglers-log_347/anglers-log_347.apk) · [metadata](cohenadair_anglers-log_347/meta.json) |
| 83 | [(NC)AnglesLog#43](https://github.com/cohenadair/anglers-log/issues/43) | `com.cohenadair.anglerslog` | 1.2.3 | benchmark | [complete](cohenadair_anglers-log_43/bug_report.txt) | [APK](cohenadair_anglers-log_43/anglers-log_43.apk) · [metadata](cohenadair_anglers-log_43/meta.json) |
| 84 | [(NC)Anki#5753](https://github.com/ankidroid/Anki-Android/issues/5753) | `com.ichi2.anki` | 2.9.1 | benchmark | [complete](ankidroid_Anki-Android_5753/bug_report.txt) | [APK](ankidroid_Anki-Android_5753/Anki-Android_5753.apk) · [metadata](ankidroid_Anki-Android_5753/meta.json) |
| 85 | [(NC)FieldBook#137 *](https://github.com/PhenoApps/Field-Book/issues/137) | `com.fieldbook.tracker` | 4.3.3 | benchmark | [complete](PhenoApps_Field-Book_137/bug_report.txt) | [APK](PhenoApps_Field-Book_137/Field-Book_137.apk) · [metadata](PhenoApps_Field-Book_137/meta.json) |
| 86 | [(NC)Gpstest#404](https://github.com/barbeau/gpstest/issues/404) | `com.android.gpstest` | 3.6.4 | benchmark | [complete](barbeau_gpstest_404/bug_report.txt) | [APK](barbeau_gpstest_404/gpstest_404.apk) · [metadata](barbeau_gpstest_404/meta.json) |
| 87 | [(NC)Images2PDF#154](https://github.com/Swati4star/Images-to-PDF/issues/154) | `swati4star.createpdf` | 2.5 | benchmark | [complete](Swati4star_Images-to-PDF_154/bug_report.txt) | [APK](Swati4star_Images-to-PDF_154/Images-to-PDF_154.apk) · [metadata](Swati4star_Images-to-PDF_154/meta.json) |
| 88 | [(NC)K9#3971](https://github.com/thunderbird/thunderbird-android/issues/3971) | `com.fsck.k9` | 5.700 | benchmark | [complete](thunderbird_thunderbird-android_3971/bug_report.txt) | [APK](thunderbird_thunderbird-android_3971/thunderbird-android_3971.apk) · [metadata](thunderbird_thunderbird-android_3971/meta.json) |
| 89 | [(NC)KISS#1481*](https://github.com/Neamar/KISS/issues/1481) | `fr.neamar.kiss.debug` | 3.13.5 | benchmark | [complete](Neamar_KISS_1481/bug_report.txt) | [APK](Neamar_KISS_1481/KISS_1481.apk) · [metadata](Neamar_KISS_1481/meta.json) |
| 90 | [(NC)LrkFM#34 *](https://github.com/lfuelling/lrkFM/issues/34) | `io.lerk.lrkFM` | 2.0.2 | benchmark | [complete](lfuelling_lrkFM_34/bug_report.txt) | [APK](lfuelling_lrkFM_34/lrkFM_34.apk) · [metadata](lfuelling_lrkFM_34/meta.json) |
| 91 | [(NC)Markor#1020](https://github.com/gsantner/markor/issues/1020) | `net.gsantner.markor` | 2.3.1 | benchmark | [complete](gsantner_markor_1020/bug_report.txt) | [APK](gsantner_markor_1020/markor_1020.apk) · [metadata](gsantner_markor_1020/meta.json) |
| 92 | [(NC)Markor#331](https://github.com/gsantner/markor/issues/331) | `net.gsantner.markor` | 1.0.2 | benchmark | [complete](gsantner_markor_331/bug_report.txt) | [APK](gsantner_markor_331/markor_331.apk) · [metadata](gsantner_markor_331/meta.json) |
| 93 | [(NC)Memento#7](https://github.com/alexstyl/Memento-Calendar/issues/7) | `com.alexstyl.specialdates` | 3.6 | benchmark | [complete](alexstyl_Memento-Calendar_7/bug_report.txt) | [APK](alexstyl_Memento-Calendar_7/Memento-Calendar_7.apk) · [metadata](alexstyl_Memento-Calendar_7/meta.json) |
| 94 | [(NC)Qksms#1124](https://github.com/moezbhatti/qksms/issues/1124) | `com.moez.QKSMS` | 3.1.3 | benchmark | [complete](moezbhatti_qksms_1124/bug_report.txt) | [APK](moezbhatti_qksms_1124/qksms_1124.apk) · [metadata](moezbhatti_qksms_1124/meta.json) |
| 95 | [(NC)Qksms#1155*](https://github.com/moezbhatti/qksms/issues/1155) | `com.moez.QKSMS` | 3.2.0 | benchmark | [complete](moezbhatti_qksms_1155/bug_report.txt) | [APK](moezbhatti_qksms_1155/qksms_1155.apk) · [metadata](moezbhatti_qksms_1155/meta.json) |
| 96 | [(NC)WiFiAnalyzer#222](https://github.com/VREMSoftwareDevelopment/WiFiAnalyzer/issues/222) | `com.vrem.wifianalyzer` | 2.0.3 | benchmark | [complete](VREMSoftwareDevelopment_WiFiAnalyzer_222/bug_report.txt) | [APK](VREMSoftwareDevelopment_WiFiAnalyzer_222/WiFiAnalyzer_222.apk) · [metadata](VREMSoftwareDevelopment_WiFiAnalyzer_222/meta.json) |

## Source acknowledgments

Artifacts retain their upstream licenses; this dataset does not relicense them.
Source URLs, exact repository commits and Git blob IDs are recorded where available.

- [ReBL](https://github.com/datareviewtest/ReBL)
- [AndroR2+](https://github.com/se-umn/2022_saner_bug_report_reproduction_study)
- [AndroR2](https://github.com/SageSELab/AndroR2)
- [ReCDroid](https://github.com/AndroidTestBugReport/ReCDroid)
- [Themis](https://github.com/the-themis-benchmarks/home)
- [ReproBot](https://github.com/USC-SQL/ReproBot-Artifact)
- [F-Droid archive](https://f-droid.org/archive/) and [ODK releases](https://github.com/getodk/collect/releases)
- [Internet Archive](https://web.archive.org/) and [Google Code Archive](https://code.google.com/archive/)
