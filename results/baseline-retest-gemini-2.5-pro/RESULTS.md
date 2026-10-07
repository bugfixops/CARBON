# AdbGPT and ReActDroid, re-run from their published code (Gemini 2.5 Pro)

| | AdbGPT | ReActDroid |
|---|---|---|
| Code | [sidongfeng/AdbGPT](https://github.com/sidongfeng/AdbGPT) @ `ec29b4b` | [wuchiuwong/ReActDroid](https://github.com/wuchiuwong/ReActDroid) @ `6bde9cd` |
| Bugs | all 100 | the 17 crash bugs (its only success signal is a crash) |
| Valid runs | 100 | 17 |
| **Reproduced (audit)** | **2 / 100** | **3 / 17** |
| Run outcomes | 64 replayed every extracted step; 36 looped on a step until the US$2.50 cap | 3 crash detected; 11 explored for the full 30 min; 3 ended in an error |
| Gemini cost of these runs | US$96.88 | US$11.93 |

These runs replace those of an earlier adaptation of the two tools, which could
not send AdbGPT's commands to the device and failed on most of ReActDroid's
pages; those runs were discarded.

## How the runs were made

- The tools' published code, with the smallest changes needed to run on Gemini
  2.5 Pro and a current Android tool chain. Every change and its reason:
  [`baselines/UPSTREAM.md`](../../baselines/UPSTREAM.md).
- One CI job per run on a GitHub-hosted runner, each on a fresh Pixel 4 /
  Android 14 (API 34) x86_64 emulator, driven by the harness in
  [`baselines/`](../../baselines/). Each `run.json` records the harness commit,
  device, model, budget and timings.
- Each tool's own prompts, temperature (AdbGPT 0.2, ReActDroid 0) and success
  logic; a 1,800 s budget; the same device preparation and seed media as
  CARBON (ReActDroid installs with `-g`, as its code does).
- AdbGPT runs stop once they have spent US$2.50 on the LLM; AdbGPT retries an
  unmatched step indefinitely. Time spent waiting out HTTP 429 rate limits does
  not count against the budget.
- On the CI emulators the system launcher sometimes stopped responding during
  boot, and its "isn't responding" dialog covered the app before the tool
  started. 24 AdbGPT runs were affected; the harness now closes such a dialog
  before every run, and those 24 bugs were run again. The affected runs are in
  [`excluded/adbgpt-launcher-dialog/`](excluded/adbgpt-launcher-dialog/).
- Runs that failed for infrastructure reasons (LLM rate limits that outlasted
  every retry, device-automation errors) were run again; those attempts are
  listed under [Earlier attempts](#earlier-attempts), logs only.

## Audit

AdbGPT has no success verdict of its own and ReActDroid accepts a crash in any
process, so every run was audited with the criteria in the paper: actions
reached the device, the reported trigger was performed, and the reported
symptom is visible (for a crash bug, a fatal exception or ANR in the app's own
process that matches the report). Sheets with each verdict and its evidence:
[`audit/adbgpt_audit.csv`](audit/adbgpt_audit.csv),
[`audit/reactdroid_audit.csv`](audit/reactdroid_audit.csv).

## Run folders

`<tool>/<category>/<bug>/` holds one run:

| File | Content |
|---|---|
| `run.json` | status, tool claim, timings, LLM usage and cost, device, harness commit, app version, crashes attributed to the app's own process |
| `harness.log` | the harness's own log |
| `adbgpt_log.txt` / `reactdroid_log.txt` | the tool's full output |
| `llm_usage.jsonl` | every LLM call: tokens (thinking included), cost, retries |
| `logcat.txt.gz` | full logcat (main, system, crash buffers) with PIDs |
| `final.jpg` | the screen when the run ended |
| `adbgpt_output/` | AdbGPT's per-step screenshots and view hierarchies, and its own log |
| `reactdroid_data/` | ReActDroid's states (screenshots and hierarchies), page prompts and chat logs |

Screenshots are stored as JPEG; step screenshots at 540 px width. The Google
Cloud project id is redacted from the logs.

## AdbGPT (100 bugs)

| Bug | Category | Crash bug | Run status | Audit | Reason | Run |
|---|---|---|---|---|---|---|
| `A-EDev_Flow_27` | swipe | no | finished | ❌ | 'video' not found 3x -> BACK on permission/update dialogs (step_0_missing_0..2.png); then tapped a video and the fullscreen button (step_1.png; playe… | [folder](adbgpt/swipe/A-EDev_Flow_27) |
| `A-EDev_Flow_284` | swipe | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.53). Extracted [Tap] video, [Tap] play button, [Double tap] video, [Scroll] up. 'video' never matched: BACK on notif… | [folder](adbgpt/swipe/A-EDev_Flow_284) |
| `Anthonyy232_Paperize_325` | long_press | yes | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.57). 0 app actions; every step 'No component found' -> BACK (43x); final.png = Android home screen (app left). Crash… | [folder](adbgpt/long_press/Anthonyy232_Paperize_325) |
| `Anthonyy232_Paperize_426` | scroll | no | finished | ❌ | LLM extracted no S2R entities (rotation is not an AdbGPT action); zero actions executed (adbgpt_output holds only loguru.log). final.png = Paperize p… | [folder](adbgpt/scroll/Anthonyy232_Paperize_426) |
| `CodeWorksCreativeHub_mLauncher_809` | swipe | no | finished | ❌ | Never reached the home screen: [Tap] 'homescreen' was a [MISSING]-guessed tap on onboarding NEXT (step_0.png); [Scroll] "Up" executed as swipe 540,19… | [folder](adbgpt/swipe/CodeWorksCreativeHub_mLauncher_809) |
| `Crustack_NotallyX_570` | long_press | yes | finished | ❌ | Crash bug; no FATAL/ANR for com.philkes.notallyx (only a uiautomator ToastActivity crash). Both notes were typed into one editor ('Note ANote B', ste… | [folder](adbgpt/long_press/Crustack_NotallyX_570) |
| `Droid-ify_client_238` | swipe | yes | finished | ❌ | Crash bug; no FATAL/ANR for com.looker.droidify (only uiautomator ToastActivity crash). 'settings section' and 'notify new versions toggle' were [MIS… | [folder](adbgpt/swipe/Droid-ify_client_238) |
| `Droid-ify_client_583` | swipe | no | finished | ❌ | 'preview image' was a [MISSING]-guessed tap on the status-bar notification icon (198,34; step_0.png); [Scroll] "left" executed as vertical swipe 540,… | [folder](adbgpt/swipe/Droid-ify_client_583) |
| `Fandroid745_Open-notes_15` | scroll | no | finished | ❌ | Created a note and typed only 'long text' (one line, step_1.png), so the content never exceeded the screen; the scroll swipe started on the keyboard… | [folder](adbgpt/scroll/Fandroid745_Open-notes_15) |
| `FossifyOrg_Calendar_1035` | double_tap | yes | finished | ✅ | Extracted [Tap] '+', [Tap] 'event'. Step 0 tapped calendar_fab, the big + ('New Event', 959,2093). step_1_hierarchy shows the FAB menu open with Task… | [folder](adbgpt/double_tap/FossifyOrg_Calendar_1035) |
| `FossifyOrg_Calendar_1042` | orientation | no | finished | ❌ | Rotation is not an AdbGPT action and was not extracted. 'day view' -> Change view picker (step_1.png) dismissed by [Scroll] "right" executed as a ver… | [folder](adbgpt/orientation/FossifyOrg_Calendar_1042) |
| `FossifyOrg_Calendar_1103` | swipe | no | finished | ❌ | TalkBack never enabled (impossible with AdbGPT primitives); Change-view picker opened then dismissed by a vertical swipe (step_1.png, final.png). The… | [folder](adbgpt/swipe/FossifyOrg_Calendar_1103) |
| `FossifyOrg_Calendar_153` | swipe | no | finished | ❌ | 'monthly view' tapped day 27, which opened the daily view (step_1.png); [Scroll] "right" executed as a vertical swipe 540,1980->300; no horizontal mo… | [folder](adbgpt/swipe/FossifyOrg_Calendar_153) |
| `FossifyOrg_Calendar_273` | double_tap | no | spend_cap | ❌ | spend_cap after 45 LLM calls ($2.54). A system 'Pixel Launcher isn't responding' dialog is in every hierarchy from step 0, so no component matched; 0… | [folder](adbgpt/double_tap/FossifyOrg_Calendar_273) |
| `FossifyOrg_Calendar_621` | pinch_zoom | no | finished | ❌ | LLM extracted [Tap] Weekly view, [Zoom] out, [Scroll] right. 'Error: No actions found: [Zoom] ["out"]' cut the plan to step 1. One action: tap 'Chang… | [folder](adbgpt/pinch_zoom/FossifyOrg_Calendar_621) |
| `FossifyOrg_Camera_23` | pinch_zoom | no | finished | ❌ | Only action: [Scroll] "in" executed as a vertical swipe over the camera-permission dialog (step_0.png); no pinch zoom (not an AdbGPT action); final.p… | [folder](adbgpt/pinch_zoom/FossifyOrg_Camera_23) |
| `FossifyOrg_Camera_91` | orientation | no | finished | ❌ | Extracted tap timer, tap 10 seconds, tap shutter. The rotation step was not extracted. Two BACKs dismissed the camera-permission dialog ('Camera perm… | [folder](adbgpt/orientation/FossifyOrg_Camera_91) |
| `FossifyOrg_Clock_156` | swipe | no | finished | ❌ | Timer never started: 'Timer duration' tapped the Timer tab and 'Start' tapped OK of the timer dialog (step_0/1.png); no alarm rang; notification shad… | [folder](adbgpt/swipe/FossifyOrg_Clock_156) |
| `FossifyOrg_Clock_85` | orientation | no | finished | ❌ | Extracted '[Rotate] [landscape]' is not an AdbGPT action, so it and the following snooze step were silently dropped; only 2 taps ran and no alarm was… | [folder](adbgpt/orientation/FossifyOrg_Clock_85) |
| `FossifyOrg_Contacts_197` | orientation | no | finished | ❌ | Favorites tab selected correctly (step_0.png) but the extracted '[Rotate]' step was dropped (not an AdbGPT action); final.png still portrait Favorite… | [folder](adbgpt/orientation/FossifyOrg_Contacts_197) |
| `FossifyOrg_File-Manager_136` | scroll | no | spend_cap | ❌ | spend_cap after 45 LLM calls ($2.56). 0 app actions; every step 'No component found' -> BACK (44x); final.png = 'Please grant our app access to all y… | [folder](adbgpt/scroll/FossifyOrg_File-Manager_136) |
| `FossifyOrg_File-Manager_195` | long_press | no | spend_cap | ❌ | spend_cap after 40 LLM calls ($2.60). 3 action(s): [Tap] ['folder'] -> tap 592 1950; [Long-tap] ['ZIP file'] -> swipe 540 1217 541 1218 500; [Tap] ['… | [folder](adbgpt/long_press/FossifyOrg_File-Manager_195) |
| `FossifyOrg_Gallery_237` | swipe | no | finished | ❌ | 'video file' -> 'Select photos and videos' on the permission dialog -> system photo picker (step_1.png); two [Scroll] up swipes left the app (step_2.… | [folder](adbgpt/swipe/FossifyOrg_Gallery_237) |
| `FossifyOrg_Gallery_289` | pinch_zoom | no | finished | ❌ | 'Allow deep zooming images' -> 'Allow all' permission button; 'image' -> 'Media only'; 'back button' -> Media management settings (step_2.png); final… | [folder](adbgpt/pinch_zoom/FossifyOrg_Gallery_289) |
| `FossifyOrg_Gallery_363` | double_tap | no | finished | ❌ | Started on Gallery's media-permission dialog. Tapped 'Select photos and videos', which opened the system photo picker. The 'double tap' was two taps… | [folder](adbgpt/double_tap/FossifyOrg_Gallery_363) |
| `FossifyOrg_Gallery_584` | double_tap | yes | finished | ❌ | Crash bug. Same permission flow: tapped 'Select photos and videos', then a thumbnail in the system photo picker (177,790), which only selected it (fi… | [folder](adbgpt/double_tap/FossifyOrg_Gallery_584) |
| `FossifyOrg_Gallery_642` | pinch_zoom | no | finished | ❌ | 'photo' -> 'Select photos and videos' -> system photo picker (step_1.png, final.png); [Scroll] "right" executed vertically; the '[Double tap] [photo]… | [folder](adbgpt/pinch_zoom/FossifyOrg_Gallery_642) |
| `FossifyOrg_Gallery_678` | double_tap | no | finished | ❌ | Stuck in the system photo picker (step_1/2.png, final.png): both 'double taps' (two adb taps at 177,790) selected/deselected a picker thumbnail, not… | [folder](adbgpt/double_tap/FossifyOrg_Gallery_678) |
| `FossifyOrg_Gallery_728` | pinch_zoom | no | finished | ❌ | 'picture' -> 'Select photos and videos' -> system photo picker; two vertical swipes inside the picker (step_1/2.png, final.png). No picture opened; p… | [folder](adbgpt/pinch_zoom/FossifyOrg_Gallery_728) |
| `FossifyOrg_Gallery_846` | double_tap | no | spend_cap | ❌ | spend_cap after 45 LLM calls ($2.60). 0 app actions; every step 'No component found' -> BACK (44x); final.png = 'Fossify Gallery needs full access...… | [folder](adbgpt/double_tap/FossifyOrg_Gallery_846) |
| `FossifyOrg_Gallery_847` | double_tap | no | finished | ❌ | Both steps were [MISSING]-guessed taps on permission prompts ('Allow all', then 'All files' twice as the 'double tap'); final.png = system 'All files… | [folder](adbgpt/double_tap/FossifyOrg_Gallery_847) |
| `FossifyOrg_Gallery_940` | swipe | no | spend_cap | ❌ | spend_cap after 45 LLM calls ($2.59). 0 app actions; every step 'No component found' -> BACK (44x); final.png = 'Fossify Gallery needs full access...… | [folder](adbgpt/swipe/FossifyOrg_Gallery_940) |
| `FossifyOrg_Launcher_198` | long_press | no | spend_cap | ❌ | spend_cap after 46 LLM calls ($2.60). 0 app actions; every step 'No component found' -> BACK (45x); final.png = Android home screen. No reported symp… | [folder](adbgpt/long_press/FossifyOrg_Launcher_198) |
| `FossifyOrg_Launcher_304` | drag_and_drop | no | finished | ❌ | Long-press on the Chrome dock icon opened its menu (step_0.png); 'bottom right most location' tapped 'New tab' -> Chrome welcome screen (final.png, o… | [folder](adbgpt/drag_and_drop/FossifyOrg_Launcher_304) |
| `FossifyOrg_Launcher_66` | swipe | no | finished | ❌ | [Scroll] left/right executed as vertical swipes (opened the app drawer, step_2.png); 'folder' -> Files app -> final.png = Files 'Downloads' (other ap… | [folder](adbgpt/swipe/FossifyOrg_Launcher_66) |
| `FossifyOrg_Messages_359` | long_press | no | finished | ❌ | Set-default-SMS dialog dismissed with BACK (step_0_missing_0.png); long-press then hit the Google Messages icon on the launcher (step_0.png); 'More o… | [folder](adbgpt/long_press/FossifyOrg_Messages_359) |
| `FossifyOrg_Messages_416` | long_press | no | finished | ❌ | Both steps ran inside the 'Set Messages as your default SMS app?' role dialog: long-press (370,1125) and tap (370,1007) on the 'Messages' option. fin… | [folder](adbgpt/long_press/FossifyOrg_Messages_416) |
| `FossifyOrg_Messages_641` | long_press | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.54). BACK on the default-SMS dialog, then a tap on the empty conversation list (540,1228). The app was then gone (st… | [folder](adbgpt/long_press/FossifyOrg_Messages_641) |
| `FossifyOrg_Messages_80` | swipe | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.51). '+ icon' never matched. Two BACKs on the default-SMS dialog. At step_0_missing_2 the main screen with the + FAB… | [folder](adbgpt/swipe/FossifyOrg_Messages_80) |
| `FossifyOrg_Notes_190` | swipe | yes | finished | ❌ | Crash bug; no FATAL/ANR for org.fossify.notes. Note was empty (no long note); search typed 'any text' (step_1.png); [Scroll] "right" executed as a ve… | [folder](adbgpt/swipe/FossifyOrg_Notes_190) |
| `FossifyOrg_Notes_59` | drag_and_drop | no | finished | ❌ | Typed 'item 1item 2' into the 'Add a new note' label field (step_2.png); 'checkbox' tapped the Checklist radio, 'Sort by' hit the keyboard toolbar an… | [folder](adbgpt/drag_and_drop/FossifyOrg_Notes_59) |
| `FossifyOrg_Paint_125` | pinch_zoom | no | finished | ❌ | Extraction answer used '1. ' numbering with entities on separate lines, so the parser found 0 steps; zero actions executed (adbgpt_output holds only… | [folder](adbgpt/pinch_zoom/FossifyOrg_Paint_125) |
| `FossifyOrg_Paint_25` | pinch_zoom | no | finished | ❌ | Drew a line (step_0 swipe), tapped the stroke-width bar centre (not minimum) and the eraser, erased with a swipe (final.png). The zoom step '[Double… | [folder](adbgpt/pinch_zoom/FossifyOrg_Paint_25) |
| `Kin69_EasyNotes_356` | swipe | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.60). The split-screen steps were dropped by extraction. '[Input] note text' only tapped 'New Note' (745,2093); no te… | [folder](adbgpt/swipe/Kin69_EasyNotes_356) |
| `LawnchairLauncher_lawnchair_1247` | drag_and_drop | yes | finished | ❌ | Crash bug; no FATAL/ANR for app.lawnchair. TalkBack 'Move' action never used; long-press on At-a-Glance 'Tap to set up' -> Customize -> At a Glance s… | [folder](adbgpt/drag_and_drop/LawnchairLauncher_lawnchair_1247) |
| `LawnchairLauncher_lawnchair_2910` | double_tap | no | finished | ❌ | The accessibility prompt shown is normal behaviour on a device without root; the bug (double tap no longer uses root) cannot be distinguished on the… | [folder](adbgpt/double_tap/LawnchairLauncher_lawnchair_2910) |
| `LawnchairLauncher_lawnchair_4125` | double_tap | no | finished | ❌ | 'settings'/'gestures'/'double tap to sleep'/'kebab menu' mapped to At-a-Glance 'Tap to Set Up', 'Change Settings' and the 'General' header (steps 0-3… | [folder](adbgpt/double_tap/LawnchairLauncher_lawnchair_4125) |
| `LawnchairLauncher_lawnchair_4320` | drag_and_drop | yes | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.57). 0 app actions; every step 'No component found' -> BACK (43x); final.png = Lawnchair home screen. Crash bug: no… | [folder](adbgpt/drag_and_drop/LawnchairLauncher_lawnchair_4320) |
| `LawnchairLauncher_lawnchair_4642` | swipe | no | finished | ❌ | LLM returned '(None)' S2R entities (orientation change and launcher restart are not AdbGPT actions); zero actions executed; final.png = Lawnchair hom… | [folder](adbgpt/swipe/LawnchairLauncher_lawnchair_4642) |
| `LawnchairLauncher_lawnchair_4708` | swipe | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.57). 2 action(s): [Scroll] ['home bar'] ['up'] -> swipe 540 1980 541 300 500; [Scroll] ['home bar'] ['up'] -> swipe… | [folder](adbgpt/swipe/LawnchairLauncher_lawnchair_4708) |
| `LawnchairLauncher_lawnchair_4786` | double_tap | yes | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.57). 0 app actions; every step 'No component found' -> BACK (42x); final.png = Lawnchair home screen. Crash bug: no… | [folder](adbgpt/double_tap/LawnchairLauncher_lawnchair_4786) |
| `LawnchairLauncher_lawnchair_5496` | swipe | yes | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.50). 1 action(s): [Tap] ['any app'] -> tap 928 1809; then 'No component found' -> BACK 40x; final.png = Lawnchair ho… | [folder](adbgpt/swipe/LawnchairLauncher_lawnchair_5496) |
| `LawnchairLauncher_lawnchair_5540` | quick_tap | no | finished | ❌ | Only one home page exists and no default page was set; [Scroll] "left" executed vertically (opened the drawer, step_1_missing_0.png); 'home button' =… | [folder](adbgpt/quick_tap/LawnchairLauncher_lawnchair_5540) |
| `MetrolistGroup_Metrolist_3227` | drag_and_drop | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.60). Only step extracted: [Long tap] 'new song'. BACK on notification-permission dialog and Changelog sheet. Then th… | [folder](adbgpt/drag_and_drop/MetrolistGroup_Metrolist_3227) |
| `MetrolistGroup_Metrolist_3391` | swipe | no | finished | ❌ | Finished. The Changelog bottom sheet covered the app throughout. 'song' and 'mini-player' were both mapped to a changelog text line (tap 560,2183). '… | [folder](adbgpt/swipe/MetrolistGroup_Metrolist_3391) |
| `MetrolistGroup_Metrolist_3561` | drag_and_drop | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.60). 'sort button' never matched. BACK on notification dialog and Changelog. Then the Home screen was visible, but i… | [folder](adbgpt/drag_and_drop/MetrolistGroup_Metrolist_3561) |
| `NeoApplications_Neo-Launcher_130` | drag_and_drop | no | spend_cap | ❌ | Logcat FATAL EXCEPTION in com.saggitt.omega:wallpaper_chooser (ColorExtractionService, SecurityException READ_EXTERNAL_STORAGE): the app's own sub-pr… | [folder](adbgpt/drag_and_drop/NeoApplications_Neo-Launcher_130) |
| `OuterTune_OuterTune_1044` | swipe | no | spend_cap | ❌ | spend_cap after 42 LLM calls ($2.53). All 42 hierarchies and final.png show the 'Welcome to OuterTune' onboarding screen. 'playlist' never matched. 4… | [folder](adbgpt/swipe/OuterTune_OuterTune_1044) |
| `Pool-Of-Tears_GreenStash_170` | double_tap | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.60). 1 action(s): [Scroll] ['right'] -> swipe 540 1980 541 300 500; then 'No component found' -> BACK 42x; final.png… | [folder](adbgpt/double_tap/Pool-Of-Tears_GreenStash_170) |
| `TeamNewPipe_NewPipe_10750` | double_tap | yes | finished | ❌ | Crash bug (player error); no FATAL/ANR and no player error in logcat. 'video' not found 4x -> BACKs left the app; 'video' then tapped the NewPipe lau… | [folder](adbgpt/double_tap/TeamNewPipe_NewPipe_10750) |
| `TeamNewPipe_NewPipe_8338` | double_tap | no | finished | ❌ | Trending failed to load ('Sorry, something went wrong', step_0_missing_1.png, final.png); 'video' tapped the NewPipe launcher icon (step_0.png). No v… | [folder](adbgpt/double_tap/TeamNewPipe_NewPipe_8338) |
| `Waboodoo_HTTP-Shortcuts_262` | orientation | no | finished | ❌ | Tapped + and the 'Create New Shortcut' dialog is visible (final.png); both '[Rotate]' steps were dropped (not AdbGPT actions), so the dialog was neve… | [folder](adbgpt/orientation/Waboodoo_HTTP-Shortcuts_262) |
| `abdallahmehiz_mpvKt_184` | double_tap | no | finished | ❌ | All three steps (incl. the 'double tap') tapped the 'mpvKt' toolbar title at 285,153 on the start screen (step_0-2.png); no video was opened (final.p… | [folder](adbgpt/double_tap/abdallahmehiz_mpvKt_184) |
| `anilbeesetti_nextplayer_1127` | swipe | no | finished | ❌ | 'video' -> 'Select photos and videos' -> system photo picker (step_1.png, final.png); no video opened in landscape; the 'swipe down from top' was a f… | [folder](adbgpt/swipe/anilbeesetti_nextplayer_1127) |
| `anilbeesetti_nextplayer_1389` | quick_tap | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.58). 0 app actions; every step 'No component found' -> BACK (43x); final.png = Android home screen (app left). No re… | [folder](adbgpt/quick_tap/anilbeesetti_nextplayer_1389) |
| `ankidroid_Anki-Android_14934` | swipe | no | finished | ❌ | TalkBack never enabled; 'deck' -> 'Get Started' (onboarding), then two vertical swipes on the 'AnkiDroid needs some permissions' screen (step_1/2.png… | [folder](adbgpt/swipe/ankidroid_Anki-Android_14934) |
| `ankidroid_Anki-Android_16135` | pinch_zoom | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.59). 'Statistics' never matched on the 'Study less / Get Started' intro screen. The first BACK exited to the launche… | [folder](adbgpt/pinch_zoom/ankidroid_Anki-Android_16135) |
| `ankidroid_Anki-Android_16410` | orientation | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.58). Rotation is unsupported ('Error: No actions found: [Rotate]'). 'statistics' never matched on the intro screen.… | [folder](adbgpt/orientation/ankidroid_Anki-Android_16410) |
| `ankidroid_Anki-Android_17393` | double_tap | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.50). 0 app actions; every step 'No component found' -> BACK (42x); final.png = Android home screen (app left). No re… | [folder](adbgpt/double_tap/ankidroid_Anki-Android_17393) |
| `ankidroid_Anki-Android_17667` | pinch_zoom | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.59). 0 app actions; every step 'No component found' -> BACK (42x); final.png = Android home screen (app left). No re… | [folder](adbgpt/pinch_zoom/ankidroid_Anki-Android_17667) |
| `ankidroid_Anki-Android_18529` | quick_tap | yes | spend_cap | ❌ | Crash bug. spend_cap after 43 LLM calls ($2.54). BACK exited the intro screen to the launcher. '[Long tap] deck' was executed on the launcher's AnkiD… | [folder](adbgpt/quick_tap/ankidroid_Anki-Android_18529) |
| `ankidroid_Anki-Android_19641` | quick_tap | no | finished | ❌ | Stuck in onboarding: 'Get Started', then the disabled 'Continue' on the All-files permission screen (step_1.png, final.png). No study screen; rapid a… | [folder](adbgpt/quick_tap/ankidroid_Anki-Android_19641) |
| `ankidroid_Anki-Android_20789` | quick_tap | no | finished | ❌ | Finished. Only extracted step: [Scroll] up (swipe 540,442 to 541,1980) on the intro screen. final.png = intro screen. No collection, no sync (no Anki… | [folder](adbgpt/quick_tap/ankidroid_Anki-Android_20789) |
| `ankidroid_Anki-Android_5512` | scroll | no | finished | ❌ | LLM extracted 4 steps but numbered them '1. [Tap]' (two spaces), which the parser rejects; zero actions executed (final.png = notification-permission… | [folder](adbgpt/scroll/ankidroid_Anki-Android_5512) |
| `ankidroid_Anki-Android_5544` | scroll | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.55). 0 app actions; every step 'No component found' -> BACK (42x); final.png = Android home screen (app left). No re… | [folder](adbgpt/scroll/ankidroid_Anki-Android_5544) |
| `ankidroid_Anki-Android_7138` | quick_tap | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.59). 1 action(s): [Tap] ['answer button'] -> tap 540 1214; then 'No component found' -> BACK 42x; final.png = 'Welco… | [folder](adbgpt/quick_tap/ankidroid_Anki-Android_7138) |
| `bartoostveen_ViTune_710` | swipe | no | finished | ❌ | Quick picks only showed loading skeletons (step_0.png); 'song' -> Songs tab (empty); no song played; the 'swipe down' was a finger-up swipe; notifica… | [folder](adbgpt/swipe/bartoostveen_ViTune_710) |
| `breezy-weather_breezy-weather_1639` | long_press | yes | finished | ❌ | Crash/freeze bug (launcher); no FATAL/ANR in logcat. 3 BACKs, then 'weather wallpaper' tapped the Breezy launcher icon and 'dynamic wallpaper' tapped… | [folder](adbgpt/long_press/breezy-weather_breezy-weather_1639) |
| `breezy-weather_breezy-weather_205` | swipe | no | finished | ❌ | 'Add current location' opened the provider dialog (step_2.png); [Scroll] "left" executed as a vertical swipe (dismissed it); the list stayed empty (s… | [folder](adbgpt/swipe/breezy-weather_breezy-weather_205) |
| `breezy-weather_breezy-weather_2159` | drag_and_drop | yes | finished | ❌ | Crash bug (launcher crash); no FATAL/ANR in logcat. All 4 steps were [MISSING]-guessed actions inside Breezy (long-press on the toolbar button, taps… | [folder](adbgpt/drag_and_drop/breezy-weather_breezy-weather_2159) |
| `breezy-weather_breezy-weather_85` | swipe | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.55). 1 action(s): [Tap] ['settings'] -> tap 540 1115; then 'No component found' -> BACK 41x; final.png = 'Access loc… | [folder](adbgpt/swipe/breezy-weather_breezy-weather_85) |
| `cromaguy_Rhythm_281` | double_tap | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.54). The first hierarchy was the splash/loading screen (only the clock). 'Next Button' not found, so BACK exited to… | [folder](adbgpt/double_tap/cromaguy_Rhythm_281) |
| `dessalines_thumb-key_371` | swipe | no | finished | ❌ | Finished. '[Long tap] letter' was a long-press on the text of the Google developer-verification dialog (540,1079). '[Scroll] up' was a swipe on that… | [folder](adbgpt/swipe/dessalines_thumb-key_371) |
| `espresso3389_methings_34` | long_press | no | finished | ❌ | Finished. The LLM answer listed [Long-tap] image and [Tap] Select Text, but in markdown list format. The extractor parsed 0 steps (no '>>>> STEP' lin… | [folder](adbgpt/long_press/espresso3389_methings_34) |
| `fast4x_RiMusic_1152` | double_tap | no | finished | ❌ | Quick picks never loaded (skeleton placeholders); both steps tapped 'By Most played song' at 378,396 with no effect (step_0/1.png, final.png). Player… | [folder](adbgpt/double_tap/fast4x_RiMusic_1152) |
| `fcitx5-android_fcitx5-android_841` | drag_and_drop | yes | finished | ❌ | Crash bug; no FATAL/ANR for org.fcitx.fcitx5.android. RIME addon not installed; tapped 'ENABLE INPUT METHOD' and 'Fcitx5' in system settings and long… | [folder](adbgpt/drag_and_drop/fcitx5-android_fcitx5-android_841) |
| `gsantner_markor_2746` | double_tap | no | spend_cap | ❌ | spend_cap after 47 LLM calls ($2.52). 0 app actions; every step 'No component found' -> BACK (45x); final.png = Markor onboarding 'Main View' page. N… | [folder](adbgpt/double_tap/gsantner_markor_2746) |
| `iamrasel_lunar-launcher_82` | swipe | yes | finished | ❌ | Crash bug; no FATAL/ANR for rasel.lunar.launcher. The only action was [Scroll] "up" = swipe 540,442->1980 (finger moving DOWN) on the launcher (final… | [folder](adbgpt/swipe/iamrasel_lunar-launcher_82) |
| `libre-tube_LibreTube_8245` | swipe | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.60). App home showed 'Nothing here.' (no content loaded). BACK went to the launcher. 'any item' then tapped the laun… | [folder](adbgpt/swipe/libre-tube_LibreTube_8245) |
| `msasikanth_twine_1566` | swipe | no | spend_cap | ❌ | spend_cap after 44 LLM calls ($2.52). 'Post' never matched on the 'Twine / GET STARTED' onboarding screen. BACK went to the launcher. 42 BACKs and 0… | [folder](adbgpt/swipe/msasikanth_twine_1566) |
| `netmackan_ATimeTracker_124` | scroll | no | finished | ❌ | Report has no steps. The overflow menu opened (step_1.png) and all 8 items fit on screen; the [Scroll] swipe started at 540,1980, outside the menu, a… | [folder](adbgpt/scroll/netmackan_ATimeTracker_124) |
| `openboard-team_openboard_613` | double_tap | no | spend_cap | ❌ | spend_cap after 43 LLM calls ($2.53). 1 action(s): [Tap] ['Openboard'] -> tap 540 253; then 'No component found' -> BACK 40x; final.png = Android hom… | [folder](adbgpt/double_tap/openboard-team_openboard_613) |
| `openboard-team_openboard_758` | double_tap | no | finished | ❌ | TalkBack never enabled; 'Open Board settings' -> 'Get started', 'settings section' -> 'Enable in Settings' -> system On-screen keyboard page (final.p… | [folder](adbgpt/double_tap/openboard-team_openboard_758) |
| `saber-notes_saber_192` | pinch_zoom | no | finished | ❌ | Opened Whiteboard and tapped the page once with the pen, which drew a dot (step_1.png, final.png). The zoom ('[Double tap]') and two-finger pan steps… | [folder](adbgpt/pinch_zoom/saber-notes_saber_192) |
| `streetcomplete_StreetComplete_6068` | pinch_zoom | yes | finished | ❌ | Crash bug (OOM); no FATAL/ANR in logcat. Stuck on the 'Welcome to OpenStreetMap' onboarding in every screenshot and final.png; taps at zoom-out/menu… | [folder](adbgpt/pinch_zoom/streetcomplete_StreetComplete_6068) |
| `syt0r_Kanji-Dojo_291` | double_tap | no | finished | ❌ | No deck existed ('Create deck by clicking on +', step_1.png); 'diagonal arrow' opened Select Deck; the 'double-tap back arrow' hit the sync icon at 8… | [folder](adbgpt/double_tap/syt0r_Kanji-Dojo_291) |
| `yairm210_Unciv_13517` | quick_tap | no | finished | ❌ | Report has only template steps; LLM extracted no S2R entities; zero actions executed (final.png = Unciv language picker in landscape). | [folder](adbgpt/quick_tap/yairm210_Unciv_13517) |
| `you-apps_ClockYou_85` | swipe | no | spend_cap | ❌ | The reported trigger (switching tabs, then BACK) was never performed. | [folder](adbgpt/swipe/you-apps_ClockYou_85) |
| `you-apps_ConnectYou_155` | swipe | no | spend_cap | ✅ | Tapped the search bar; AdbGPT's recovery BACK, pressed while search was active, quit the app (the reported behaviour). Trigger accidental but perform… | [folder](adbgpt/swipe/you-apps_ConnectYou_155) |
| `you-apps_WallYou_216` | pinch_zoom | no | finished | ❌ | 'picture' was guessed as the status-bar notification icon (tap 198,34; step_0.png); the '[Double tap]' step was dropped by the parser; no picture ope… | [folder](adbgpt/pinch_zoom/you-apps_WallYou_216) |

## ReActDroid (17 crash bugs)

| Bug | Category | Crash bug | Run status | Audit | Reason | Run |
|---|---|---|---|---|---|---|
| `Anthonyy232_Paperize_325` | long_press | yes | error | ❌ | status error: 146 actions over 29 min (Wallpaper/Library tabs, New Album dialogs) then ReActDroid itself crashed (KeyError: 1 in perform_chat). No FA… | [folder](reactdroid/long_press/Anthonyy232_Paperize_325) |
| `Crustack_NotallyX_570` | long_press | yes | finished | ✅ | Step 78 long-press selected a note, step 79 typed 'HelloWorld!' into the search, step 81 long-pressed the note in the filtered list -> logcat 14:45:4… | [folder](reactdroid/long_press/Crustack_NotallyX_570) |
| `Droid-ify_client_238` | swipe | yes | finished | ✅ | Opened Settings, set Theme=Dark, toggled Material You (one of the toggles the report names; activity relaunched). Step 6 'Click[Personalization]' act… | [folder](reactdroid/swipe/Droid-ify_client_238) |
| `FossifyOrg_Calendar_1035` | double_tap | yes | finished | ✅ | Step 1 Click[New Event] (the big +) showed Task/Event (backup 10-06_14-27-51.png); step 2 Click[Event] -> logcat 14:27:58.954 FATAL EXCEPTION in org.… | [folder](reactdroid/double_tap/FossifyOrg_Calendar_1035) |
| `FossifyOrg_Gallery_584` | double_tap | yes | timeout | ❌ | Newest run (ci_reactdroid3, timeout): only 2 actions ('Show all folders content', a 00:00 video thumbnail), then 600+ steps stuck in 'out of app' rec… | [folder](reactdroid/double_tap/FossifyOrg_Gallery_584) |
| `FossifyOrg_Notes_190` | swipe | yes | timeout | ❌ | timeout after 199 actions (53 Click[Search], 28 search inputs, opening/closing notes). ReActDroid has no swipe action (only Click/Long press/Input/Ba… | [folder](reactdroid/swipe/FossifyOrg_Notes_190) |
| `LawnchairLauncher_lawnchair_1247` | drag_and_drop | yes | timeout | ❌ | timeout after 165 actions (long-press icons/widgets, Customize, Widgets, folders); TalkBack 'Move' action never used; no FATAL/ANR for app.lawnchair;… | [folder](reactdroid/drag_and_drop/LawnchairLauncher_lawnchair_1247) |
| `LawnchairLauncher_lawnchair_4320` | drag_and_drop | yes | timeout | ❌ | timeout after 199 actions (Widgets, Customize, long-press 'Tap to set up'/Phone); no widget dragged onto the home screen (no drag action exists); no… | [folder](reactdroid/drag_and_drop/LawnchairLauncher_lawnchair_4320) |
| `LawnchairLauncher_lawnchair_4786` | double_tap | yes | timeout | ❌ | timeout after 156 actions; TalkBack never enabled, so the TalkBack 'move item' action was never used; no FATAL/ANR for app.lawnchair; final.png = hom… | [folder](reactdroid/double_tap/LawnchairLauncher_lawnchair_4786) |
| `LawnchairLauncher_lawnchair_5496` | swipe | yes | timeout | ❌ | timeout after 170 actions (Customize sheets, long-presses, folders); Recents never opened (no Recents/gesture action); no FATAL/ANR for app.lawnchair… | [folder](reactdroid/swipe/LawnchairLauncher_lawnchair_5496) |
| `TeamNewPipe_NewPipe_10750` | double_tap | yes | timeout | ❌ | timeout after 178 actions; every playback attempt hit NewPipe's ErrorActivity with ContentNotAvailableException 'Sign in to confirm that you're not a… | [folder](reactdroid/double_tap/TeamNewPipe_NewPipe_10750) |
| `ankidroid_Anki-Android_18529` | quick_tap | yes | timeout | ❌ | Newest run (ci_reactdroid3, timeout): 166 actions (menus, drawer, dialogs); taps are seconds apart, so 'touch buttons during animations' was never do… | [folder](reactdroid/quick_tap/ankidroid_Anki-Android_18529) |
| `breezy-weather_breezy-weather_1639` | long_press | yes | timeout | ❌ | timeout: 17 actions reached Settings > 'Widgets & Live wallpaper' and the system live-wallpaper picker (final.png 'Set wallpaper'), then 600+ out-of-… | [folder](reactdroid/long_press/breezy-weather_breezy-weather_1639) |
| `breezy-weather_breezy-weather_2159` | drag_and_drop | yes | timeout | ❌ | timeout after 150 actions (92 of them Back); stayed inside Breezy (Locations); never long-pressed the home screen or dragged a widget; no launcher or… | [folder](reactdroid/drag_and_drop/breezy-weather_breezy-weather_2159) |
| `fcitx5-android_fcitx5-android_841` | drag_and_drop | yes | error | ❌ | status error: UiAutomator2 instrumentation crashed after 3 actions (ENABLE INPUT METHOD, NEXT, SELECT INPUT METHOD). RIME addon not installed, no dra… | [folder](reactdroid/drag_and_drop/fcitx5-android_fcitx5-android_841) |
| `iamrasel_lunar-launcher_82` | swipe | yes | error | ❌ | status error: 1 action (Back), then ~200 'empty page' recover steps with the app force-stopped and relaunched every ~4 s ('Force stopping rasel.lunar… | [folder](reactdroid/swipe/iamrasel_lunar-launcher_82) |
| `streetcomplete_StreetComplete_6068` | pinch_zoom | yes | timeout | ❌ | timeout after 243 actions (Zoom out x44, Zoom in x34, Menu, Overlays) on the map; no pinch and no completed manual download; no OutOfMemoryError/FATA… | [folder](reactdroid/pinch_zoom/streetcomplete_StreetComplete_6068) |

## Excluded runs

| Tool | Bug | Reason | Folder |
|---|---|---|---|
| adbgpt | `A-EDev_Flow_284` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/A-EDev_Flow_284) |
| adbgpt | `FossifyOrg_Calendar_1035` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Calendar_1035) |
| adbgpt | `FossifyOrg_Calendar_621` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Calendar_621) |
| adbgpt | `FossifyOrg_Camera_91` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Camera_91) |
| adbgpt | `FossifyOrg_Gallery_363` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Gallery_363) |
| adbgpt | `FossifyOrg_Gallery_584` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Gallery_584) |
| adbgpt | `FossifyOrg_Messages_416` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Messages_416) |
| adbgpt | `FossifyOrg_Messages_641` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Messages_641) |
| adbgpt | `FossifyOrg_Messages_80` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/FossifyOrg_Messages_80) |
| adbgpt | `Kin69_EasyNotes_356` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/Kin69_EasyNotes_356) |
| adbgpt | `MetrolistGroup_Metrolist_3227` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/MetrolistGroup_Metrolist_3227) |
| adbgpt | `MetrolistGroup_Metrolist_3391` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/MetrolistGroup_Metrolist_3391) |
| adbgpt | `MetrolistGroup_Metrolist_3561` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/MetrolistGroup_Metrolist_3561) |
| adbgpt | `OuterTune_OuterTune_1044` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/OuterTune_OuterTune_1044) |
| adbgpt | `ankidroid_Anki-Android_16135` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/ankidroid_Anki-Android_16135) |
| adbgpt | `ankidroid_Anki-Android_16410` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/ankidroid_Anki-Android_16410) |
| adbgpt | `ankidroid_Anki-Android_18529` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/ankidroid_Anki-Android_18529) |
| adbgpt | `ankidroid_Anki-Android_20789` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/ankidroid_Anki-Android_20789) |
| adbgpt | `cromaguy_Rhythm_281` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/cromaguy_Rhythm_281) |
| adbgpt | `dessalines_thumb-key_371` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/dessalines_thumb-key_371) |
| adbgpt | `espresso3389_methings_34` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/espresso3389_methings_34) |
| adbgpt | `libre-tube_LibreTube_8245` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/libre-tube_LibreTube_8245) |
| adbgpt | `msasikanth_twine_1566` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/msasikanth_twine_1566) |
| adbgpt | `you-apps_ConnectYou_155` | started under the launcher’s “isn’t responding” dialog; run again | [folder](excluded/adbgpt-launcher-dialog/you-apps_ConnectYou_155) |
| reactdroid | `Anthonyy232_Paperize_325` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/Anthonyy232_Paperize_325/20261006_134306_850) |
| reactdroid | `Crustack_NotallyX_570` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/Crustack_NotallyX_570/20261006_134255_631) |
| reactdroid | `Droid-ify_client_238` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/Droid-ify_client_238/20261006_134246_720) |
| reactdroid | `FossifyOrg_Calendar_1035` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/FossifyOrg_Calendar_1035/20261006_134252_380) |
| reactdroid | `FossifyOrg_Gallery_584` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/FossifyOrg_Gallery_584/20261006_143129_593) |
| reactdroid | `ankidroid_Anki-Android_18529` | earlier run with an older harness (before later harness fixes); superseded by the run above | [folder](excluded/reactdroid-superseded/ankidroid_Anki-Android_18529/20261006_153804_400) |

### Earlier attempts

Every other run of the retest is kept too, logs only, so the folder
holds all 77 remaining attempts. They come from sweeps that were
stopped and repeated after a harness fix (rate-limit handling, the
uiautomator2 warm-up, the APK download fallback, the launcher and
permission fixes), or from jobs that failed before the tool started. None is
a result; each bug's result is the run in the tables above.

| Tool | Bug | What happened | Folder |
|---|---|---|---|
| adbgpt | `A-EDev_Flow_27` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/A-EDev_Flow_27/37399299301_no_run_record) |
| adbgpt | `A-EDev_Flow_284` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/A-EDev_Flow_284/37399776226_20261006_013730_679) |
| adbgpt | `A-EDev_Flow_284` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/A-EDev_Flow_284/37405723626_no_run_record) |
| adbgpt | `Anthonyy232_Paperize_325` | ended `timeout`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/Anthonyy232_Paperize_325/37399776226_20261006_014322_563) |
| adbgpt | `Anthonyy232_Paperize_325` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/Anthonyy232_Paperize_325/37406029077_20261006_025248_716) |
| adbgpt | `Anthonyy232_Paperize_426` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/Anthonyy232_Paperize_426/37399299301_no_run_record) |
| adbgpt | `Droid-ify_client_238` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/Droid-ify_client_238/37399299301_no_run_record) |
| adbgpt | `Fandroid745_Open-notes_15` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/Fandroid745_Open-notes_15/37399299301_no_run_record) |
| adbgpt | `FossifyOrg_Calendar_1042` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Calendar_1042/37399299301_no_run_record) |
| adbgpt | `FossifyOrg_Calendar_1103` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Calendar_1103/37399299301_no_run_record) |
| adbgpt | `FossifyOrg_Calendar_273` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Calendar_273/37399776226_20261006_014237_725) |
| adbgpt | `FossifyOrg_Camera_23` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Camera_23/37399299301_no_run_record) |
| adbgpt | `FossifyOrg_Clock_156` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Clock_156/37399299301_no_run_record) |
| adbgpt | `FossifyOrg_File-Manager_136` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_File-Manager_136/37399776226_20261006_014105_860) |
| adbgpt | `FossifyOrg_File-Manager_195` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_File-Manager_195/37399776226_20261006_014107_340) |
| adbgpt | `FossifyOrg_File-Manager_195` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_File-Manager_195/37405723626_no_run_record) |
| adbgpt | `FossifyOrg_File-Manager_195` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_File-Manager_195/37406029077_no_run_record) |
| adbgpt | `FossifyOrg_Gallery_289` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_289/37399776226_20261006_014119_140) |
| adbgpt | `FossifyOrg_Gallery_289` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_289/37406029077_no_run_record) |
| adbgpt | `FossifyOrg_Gallery_363` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_363/37399776226_20261006_014134_685) |
| adbgpt | `FossifyOrg_Gallery_363` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_363/37406029077_no_run_record) |
| adbgpt | `FossifyOrg_Gallery_584` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_584/37399776226_20261006_014204_978) |
| adbgpt | `FossifyOrg_Gallery_846` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_846/37399776226_20261006_014501_324) |
| adbgpt | `FossifyOrg_Gallery_940` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Gallery_940/37399776226_20261006_014628_711) |
| adbgpt | `FossifyOrg_Launcher_198` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Launcher_198/37399776226_20261006_014647_875) |
| adbgpt | `FossifyOrg_Launcher_66` | ended `timeout`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Launcher_66/37399776226_20261006_014730_680) |
| adbgpt | `FossifyOrg_Messages_359` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Messages_359/37399776226_20261006_014743_942) |
| adbgpt | `FossifyOrg_Messages_416` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Messages_416/37399776226_20261006_014828_946) |
| adbgpt | `FossifyOrg_Messages_641` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Messages_641/37399776226_20261006_014852_878) |
| adbgpt | `FossifyOrg_Messages_80` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Messages_80/37399776226_20261006_014956_299) |
| adbgpt | `FossifyOrg_Notes_59` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Notes_59/37399776226_20261006_015206_119) |
| adbgpt | `FossifyOrg_Paint_25` | ended `timeout`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/FossifyOrg_Paint_25/37399776226_20261006_015626_291) |
| adbgpt | `Kin69_EasyNotes_356` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/Kin69_EasyNotes_356/37399776226_20261006_015817_314) |
| adbgpt | `LawnchairLauncher_lawnchair_1247` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_1247/37399776226_20261006_020001_804) |
| adbgpt | `LawnchairLauncher_lawnchair_2910` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_2910/37399776226_20261006_020110_145) |
| adbgpt | `LawnchairLauncher_lawnchair_4125` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_4125/37399776226_20261006_020210_410) |
| adbgpt | `LawnchairLauncher_lawnchair_4320` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_4320/37399776226_20261006_020651_717) |
| adbgpt | `LawnchairLauncher_lawnchair_4642` | ended `finished`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_4642/37399776226_20261006_020709_327) |
| adbgpt | `LawnchairLauncher_lawnchair_4708` | ended `timeout`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_4708/37399776226_20261006_020658_818) |
| adbgpt | `LawnchairLauncher_lawnchair_4786` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_4786/37399776226_20261006_020946_833) |
| adbgpt | `LawnchairLauncher_lawnchair_5496` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_5496/37399776226_20261006_021014_548) |
| adbgpt | `LawnchairLauncher_lawnchair_5540` | ended `finished`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/LawnchairLauncher_lawnchair_5540/37399776226_20261006_021530_215) |
| adbgpt | `MetrolistGroup_Metrolist_3227` | ended `spend_cap`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/MetrolistGroup_Metrolist_3227/37399776226_20261006_021129_420) |
| adbgpt | `MetrolistGroup_Metrolist_3391` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/MetrolistGroup_Metrolist_3391/37399776226_20261006_021108_377) |
| adbgpt | `MetrolistGroup_Metrolist_3561` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/MetrolistGroup_Metrolist_3561/37399776226_20261006_021129_011) |
| adbgpt | `NeoApplications_Neo-Launcher_130` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/NeoApplications_Neo-Launcher_130/37399776226_20261006_021109_876) |
| adbgpt | `OuterTune_OuterTune_1044` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/OuterTune_OuterTune_1044/37399776226_20261006_021206_348) |
| adbgpt | `Pool-Of-Tears_GreenStash_170` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/Pool-Of-Tears_GreenStash_170/37399776226_20261006_021301_091) |
| adbgpt | `TeamNewPipe_NewPipe_10750` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/TeamNewPipe_NewPipe_10750/37399776226_20261006_021307_936) |
| adbgpt | `TeamNewPipe_NewPipe_8338` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/TeamNewPipe_NewPipe_8338/37399776226_no_run_record) |
| adbgpt | `Waboodoo_HTTP-Shortcuts_262` | ended `finished`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/Waboodoo_HTTP-Shortcuts_262/37399776226_20261006_022016_329) |
| adbgpt | `abdallahmehiz_mpvKt_184` | ended `finished`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/abdallahmehiz_mpvKt_184/37399776226_20261006_022033_461) |
| adbgpt | `anilbeesetti_nextplayer_1127` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/anilbeesetti_nextplayer_1127/37399776226_20261006_022117_059) |
| adbgpt | `anilbeesetti_nextplayer_1389` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/anilbeesetti_nextplayer_1389/37399776226_20261006_022051_399) |
| adbgpt | `ankidroid_Anki-Android_14934` | ended `finished`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_14934/37399776226_20261006_022137_015) |
| adbgpt | `ankidroid_Anki-Android_16135` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_16135/37399776226_no_run_record) |
| adbgpt | `ankidroid_Anki-Android_16410` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_16410/37399776226_20261006_022244_315) |
| adbgpt | `ankidroid_Anki-Android_17393` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_17393/37399776226_20261006_022230_980) |
| adbgpt | `ankidroid_Anki-Android_17667` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_17667/37399776226_no_run_record) |
| adbgpt | `ankidroid_Anki-Android_18529` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_18529/37399776226_20261006_022649_374) |
| adbgpt | `ankidroid_Anki-Android_19641` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_19641/37399776226_no_run_record) |
| adbgpt | `ankidroid_Anki-Android_20789` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_20789/37399776226_no_run_record) |
| adbgpt | `ankidroid_Anki-Android_5512` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_5512/37399776226_no_run_record) |
| adbgpt | `ankidroid_Anki-Android_5544` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_5544/37399776226_20261006_022930_417) |
| adbgpt | `ankidroid_Anki-Android_7138` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/ankidroid_Anki-Android_7138/37399776226_no_run_record) |
| adbgpt | `breezy-weather_breezy-weather_1639` | ended `error`; superseded by a later run of the same bug | [folder](excluded/adbgpt-earlier-attempts/breezy-weather_breezy-weather_1639/37399776226_20261006_023030_004) |
| adbgpt | `breezy-weather_breezy-weather_205` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/breezy-weather_breezy-weather_205/37399776226_no_run_record) |
| adbgpt | `breezy-weather_breezy-weather_2159` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/breezy-weather_breezy-weather_2159/37399776226_no_run_record) |
| adbgpt | `breezy-weather_breezy-weather_85` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/breezy-weather_breezy-weather_85/37399776226_no_run_record) |
| adbgpt | `cromaguy_Rhythm_281` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/cromaguy_Rhythm_281/37399776226_no_run_record) |
| adbgpt | `dessalines_thumb-key_371` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/dessalines_thumb-key_371/37399776226_no_run_record) |
| adbgpt | `espresso3389_methings_34` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/espresso3389_methings_34/37399776226_no_run_record) |
| adbgpt | `fast4x_RiMusic_1152` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/fast4x_RiMusic_1152/37399776226_no_run_record) |
| adbgpt | `fcitx5-android_fcitx5-android_841` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/fcitx5-android_fcitx5-android_841/37399776226_no_run_record) |
| adbgpt | `gsantner_markor_2746` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/adbgpt-earlier-attempts/gsantner_markor_2746/37399776226_no_run_record) |
| reactdroid | `FossifyOrg_Gallery_584` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/reactdroid-earlier-attempts/FossifyOrg_Gallery_584/37470019800_no_run_record) |
| reactdroid | `FossifyOrg_Notes_190` | the job was cancelled or failed before the harness wrote run.json | [folder](excluded/reactdroid-earlier-attempts/FossifyOrg_Notes_190/37470019800_no_run_record) |
