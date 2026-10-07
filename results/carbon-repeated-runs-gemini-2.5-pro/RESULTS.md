# CARBON repeated runs (Gemini 2.5 Pro)

How much does CARBON's result change from run to run? Sixteen bugs, 2 per
gesture category, were drawn with a fixed seed before any re-run and without
looking at their outcomes ([`variance_cases.json`](../../baselines/harness/variance_cases.json));
15 of them were reproduced in the paper's main run. Each was run twice more
with the main run's configuration (`carbon/reproduction.py` unchanged,
`gemini-2.5-pro`, temperature 0.3, 1,800 s budget, CARBON's device preparation).
Bugs whose repeat failed got one more run per failed repeat ("extra" columns);
these are additional runs, not replacements.

| Run | Environment | Reproduced (CARBON's verdict) |
|---|---|---|
| Main run (paper) | workstation, ARM emulator | 15 / 16 |
| Repeat 1 | GitHub Actions, x86_64 emulator | 10 / 16 |
| Repeat 2 | GitHub Actions, x86_64 emulator | 11 / 16 |

Valid runs: 43 (24 declared successes).
Gemini cost per run: median US$0.44, mean US$1.24, total US$53.24.

Verdicts in this folder are **CARBON's own** (`result: success` / `fail`), or
the harness status when the run ended without one: ⏱ the 1,800 s budget ran
out, $ the per-run LLM spend cap was reached (US$3 for the repeats, US$6 for
the extra runs). The main-run column is the audited outcome from
[`../category-testing-gemini-2.5-pro/`](../category-testing-gemini-2.5-pro/);
for these 16 bugs it equals CARBON's own verdict in that run.

| Setting | Main run | Repeats |
|---|---|---|
| Machine | workstation, ARM emulator | GitHub-hosted runner, x86_64 emulator, one per run |
| Loop guard (`REBL_MAX_REPEAT`) | not present | switched off (recorded in `run.json` → `carbon_env`) |
| Target package | read from the foreground app | passed explicitly (`REBL_TARGET_PACKAGE`) |
| Launcher "isn't responding" dialog | — | closed before the run when present (`run.json` → `closed_anr_dialogs`) |

## Per bug

| Bug | Category | Main run (paper) | Repeat 1 | Repeat 2 | Extra 1 | Extra 2 |
|---|---|---|---|---|---|---|
| `cromaguy_Rhythm_281` | double_tap | ✅ | [✅](double_tap/cromaguy_Rhythm_281/repeat_1) 202s | [✅](double_tap/cromaguy_Rhythm_281/repeat_2) 190s |  |  |
| `FossifyOrg_Gallery_363` | double_tap | ✅ | [✅](double_tap/FossifyOrg_Gallery_363/repeat_1) 306s | [✅](double_tap/FossifyOrg_Gallery_363/repeat_2) 270s |  |  |
| `MetrolistGroup_Metrolist_3227` | drag_and_drop | ✅ | [$ cap](drag_and_drop/MetrolistGroup_Metrolist_3227/repeat_1) 1763s | [⏱ timeout](drag_and_drop/MetrolistGroup_Metrolist_3227/repeat_2) 1801s | [❌ fail](drag_and_drop/MetrolistGroup_Metrolist_3227/extra_1) 1798s | [⏱ timeout](drag_and_drop/MetrolistGroup_Metrolist_3227/extra_2) 1801s |
| `fcitx5-android_fcitx5-android_841` | drag_and_drop | ✅ | [❌ fail](drag_and_drop/fcitx5-android_fcitx5-android_841/repeat_1) 585s | [⏱ timeout](drag_and_drop/fcitx5-android_fcitx5-android_841/repeat_2) 1800s | [❌ fail](drag_and_drop/fcitx5-android_fcitx5-android_841/extra_1) 735s | [⏱ timeout](drag_and_drop/fcitx5-android_fcitx5-android_841/extra_2) 1802s |
| `espresso3389_methings_34` | long_press | ✅ | [✅](long_press/espresso3389_methings_34/repeat_1) 218s | [✅](long_press/espresso3389_methings_34/repeat_2) 244s |  |  |
| `FossifyOrg_Launcher_198` | long_press | ✅ | [✅](long_press/FossifyOrg_Launcher_198/repeat_1) 363s | [✅](long_press/FossifyOrg_Launcher_198/repeat_2) 260s |  |  |
| `Waboodoo_HTTP-Shortcuts_262` | orientation | ✅ | [✅](orientation/Waboodoo_HTTP-Shortcuts_262/repeat_1) 70s | [✅](orientation/Waboodoo_HTTP-Shortcuts_262/repeat_2) 52s |  |  |
| `FossifyOrg_Camera_91` | orientation | ✅ | [✅](orientation/FossifyOrg_Camera_91/repeat_1) 98s | [✅](orientation/FossifyOrg_Camera_91/repeat_2) 106s |  |  |
| `ankidroid_Anki-Android_17667` | pinch_zoom | ✅ | [✅](pinch_zoom/ankidroid_Anki-Android_17667/repeat_1) 186s | [✅](pinch_zoom/ankidroid_Anki-Android_17667/repeat_2) 198s |  |  |
| `streetcomplete_StreetComplete_6068` | pinch_zoom | ✅ | [✅](pinch_zoom/streetcomplete_StreetComplete_6068/repeat_1) 290s | [✅](pinch_zoom/streetcomplete_StreetComplete_6068/repeat_2) 176s |  |  |
| `ankidroid_Anki-Android_20789` | quick_tap | ❌ | [$ cap](quick_tap/ankidroid_Anki-Android_20789/repeat_1) 1371s | [$ cap](quick_tap/ankidroid_Anki-Android_20789/repeat_2) 1489s | [⏱ timeout](quick_tap/ankidroid_Anki-Android_20789/extra_1) 1861s | [❌ fail](quick_tap/ankidroid_Anki-Android_20789/extra_2) 1019s |
| `ankidroid_Anki-Android_7138` | quick_tap | ✅ | [$ cap](quick_tap/ankidroid_Anki-Android_7138/repeat_1) 1306s | [$ cap](quick_tap/ankidroid_Anki-Android_7138/repeat_2) 1580s | [✅](quick_tap/ankidroid_Anki-Android_7138/extra_1) 1181s | [✅](quick_tap/ankidroid_Anki-Android_7138/extra_2) 1733s |
| `ankidroid_Anki-Android_5544` | scroll | ✅ | [❌ fail](scroll/ankidroid_Anki-Android_5544/repeat_1) 748s | [$ cap](scroll/ankidroid_Anki-Android_5544/repeat_2) 1698s | [⏱ timeout](scroll/ankidroid_Anki-Android_5544/extra_1) 1802s | [⏱ timeout](scroll/ankidroid_Anki-Android_5544/extra_2) 1802s |
| `Anthonyy232_Paperize_426` | scroll | ✅ | [❌ fail](scroll/Anthonyy232_Paperize_426/repeat_1) 72s | [✅](scroll/Anthonyy232_Paperize_426/repeat_2) 62s | [✅](scroll/Anthonyy232_Paperize_426/extra_1) 74s |  |
| `Droid-ify_client_238` | swipe | ✅ | [✅](swipe/Droid-ify_client_238/repeat_1) 84s | [✅](swipe/Droid-ify_client_238/repeat_2) 106s |  |  |
| `A-EDev_Flow_27` | swipe | ✅ | [✅](swipe/A-EDev_Flow_27/repeat_1) 180s | [✅](swipe/A-EDev_Flow_27/repeat_2) 252s |  |  |

## Run folders

`<category>/<bug>/<run>/`: `run.json`, `harness.log`, `carbon_log.txt` (CARBON's
full transcript), `carbon_tokens.json` (CARBON's own token count; `run.json`
→ `llm` adds the thinking tokens and cost), `logcat.txt.gz`, `final.jpg`, and
`screenshots/` (the annotated screenshot CARBON sent at each step, as JPEG at
540 px). The Google Cloud project id is redacted from the logs.

## Excluded runs

| Bug | Reason | Folder |
|---|---|---|
| `FossifyOrg_Gallery_363` | from a dispatch cancelled to fix the launcher dialog; all 32 repeats were run again | [folder](excluded/FossifyOrg_Gallery_363/cancelled_dispatch) |
| `MetrolistGroup_Metrolist_3227` | from a dispatch cancelled to fix the launcher dialog; all 32 repeats were run again | [folder](excluded/MetrolistGroup_Metrolist_3227/cancelled_dispatch) |
| `ankidroid_Anki-Android_7138` | the emulator went offline mid-run (adb: device offline); run again | [folder](excluded/ankidroid_Anki-Android_7138/extra_2_invalid) |
| `cromaguy_Rhythm_281` | from a dispatch cancelled to fix the launcher dialog; all 32 repeats were run again | [folder](excluded/cromaguy_Rhythm_281/cancelled_dispatch) |
| `fcitx5-android_fcitx5-android_841` | from a dispatch cancelled to fix the launcher dialog; all 32 repeats were run again | [folder](excluded/fcitx5-android_fcitx5-android_841/cancelled_dispatch) |
