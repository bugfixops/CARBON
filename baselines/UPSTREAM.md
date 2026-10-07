# What changed from the published code

`AdbGPT/` and `ReActDroid/` are copies of the authors' public repositories. Every edit is marked `[CARBON-RETEST]` in the source. `./check_upstream.sh` re-downloads the pinned commits and prints the full diff.

| Tool | Upstream | Commit |
|---|---|---|
| AdbGPT | <https://github.com/sidongfeng/AdbGPT> | `ec29b4bd71f0f6469f35ad4f81b429075fb4266b` |
| ReActDroid | <https://github.com/wuchiuwong/ReActDroid> | `6bde9cdb3bed89a826c6cccde89ad7c19ef4b340` |

The earlier runs used a different copy, `OTHER_REPO/` in ReBL-Plus. It differed from these commits: its AdbGPT step parser was rewritten, and its ReActDroid kept the `TouchAction` call that current Appium no longer supports. That copy is not used here.

## Kinds of change

- **Model.** GPT-3.5 is replaced by Gemini 2.5 Pro, so every tool in the comparison uses the same model. Prompts, message history and each tool's own temperature are unchanged.
- **Environment.** The device name, Appium address and screen size come from the harness instead of being hard-coded.
- **Compatibility.** These are the smallest changes needed to run on current Appium and an Android 14 emulator.
- **Bug fix (favours the baseline).** These fix released code that contradicts the tool's own design. Without them, the tool fails for reasons that are not about its method.

## AdbGPT

| File | Kind | Change | Why |
|---|---|---|---|
| `ChatGPT.py` | Model | `get_response_from_chatgpt` sends the same message list and temperature (0.2) to Gemini through `harness/gemini_client.py`, and strips `**` from the reply | Gemini sometimes writes `**[Tap]**`; the unmodified parser then extracts zero steps |
| `cfgs.py` | Model | `OPENAI_TOKEN = <YOUR_OPENAI_KEY>` is replaced by an unused empty string; `MODEL` defaults to `gemini-2.5-pro` | The placeholder is a Python syntax error, so upstream does not import until edited |
| `utils/config.py` | Environment | `XML_SCREEN_WIDTH/HEIGHT` are read from the environment; the harness sets them from `adb shell wm size` | Upstream's README says to set them to the device size. The earlier run left 1440×2960 on a 1080×2280 Pixel 4, so its scroll swipes started off-screen |
| `main.py` | Environment | The bug report and output folder come from `ADBGPT_BUG_REPORT` / `ADBGPT_SAVE_PATH`; the `os.path.jpon` typo is fixed | Upstream hard-codes a demo report, and the typo crashes on start |
| `extract_step.py` | Bug fix | The step regex accepts `-`, `Double-tap`/`Long-tap` are normalised to `double tap`/`long tap`, and a step with no recognised action is skipped instead of returning a bare `None` | AdbGPT's own prompt defines `[Double-tap]` and `[Long-tap]`, but the released parser cannot read them. Tested on the unmodified code: a `[Double-tap]` at step 2 silently drops every later step, and an action outside the list raises `TypeError` and ends the run |

Unchanged on purpose:
- **One growing conversation.** AdbGPT's replay keeps one conversation for the whole run, re-sending every earlier step. That's the tool's design, so it stays. Gemini's long context lets it run much longer than GPT-3.5 could, so the harness adds a per-run spend cap.
- **Failed taps.** When a step cannot be found, AdbGPT taps its best guess and retries the same step, with no limit. The shared 30-minute budget is the only stop.
- **Bare `adb`.** `adb.py` still calls bare `adb` through `os.system`. The harness puts a real `adb` first on `PATH` and selects the emulator with `ANDROID_SERIAL`. The earlier run failed here: every command returned `sh: adb: command not found`.

## ReActDroid

| File | Kind | Change | Why |
|---|---|---|---|
| `llm/model.py` | Model | `timeout_predict` sends the same messages with temperature 0 to Gemini. The per-call limit is raised from 10 s to 180 s (`REACTDROID_LLM_TIMEOUT`) | Gemini 2.5 Pro's thinking regularly takes more than 10 s. Upstream turns a timeout into an empty reply, so a 10 s limit would leave most turns without an answer |
| `tool/environment.py` | Compatibility | `MobileBy` → `AppiumBy` (renamed); capabilities passed as `UiAutomator2Options`; `TouchAction(...).long_press(el)` → `mobile: longClickGesture` on the same element | Appium-Python-Client 1.3.0 cannot drive a current Appium server, and the UiAutomator2 driver removed the `/touch/perform` endpoint. That is what produced the earlier `UnknownCommandError`s |
| `tool/environment.py` | Compatibility | `relaunch_app`: `driver.launch_app()` → `am start -S -W <package>/<activity>` | `launch_app` was removed from Appium-Python-Client. In Appium 1.x it stopped the app and started it fresh; `am start -S` does the same, so a system screen the app left open (photo picker, permission dialog) is cleared. A plain `am start` left the photo picker in front, and one run looped 384 times |
| `tool/environment.py` | Environment | `platformVersion '7.0'` → the device's version; `emulator-5554` and `localhost:4723/wd/hub` → `ANDROID_SERIAL` / `APPIUM_URL` | Hard-coded for the authors' setup |
| `main/utils.py` | Environment | `emulator-5554` → `ANDROID_SERIAL` | Same |
| `main/run_case.py` | New file | `main/run_recdroid.py`'s `Main` class, reading the case from JSON, stopping at the 1,800 s deadline, and not calling `install_app` (the harness installs the APK the same way for every tool) | Upstream's runners read the authors' dataset CSVs |
| `main/run_case.py` | Bug fix | If the page seen at the start of a step is outside the app or empty, upstream's own recovery (`relaunch_app`) runs before `choose_action` | Upstream applies that recovery only after an action. On an out-of-app start page `choose_action` raises `KeyError('page_name')`. The earlier run hit this 1,662 times, mostly on Android's "All files access" settings screen |

Not available:
- **`FaxRes` static-analysis output.** ReActDroid can seed its page model and predict the crash page from the authors' per-app page dumps. Those exist only for their datasets. Without them, upstream builds the page model as it explores and skips crash-page prediction, which is what happens here.

Unchanged on purpose:
- **Crash check.** `check_crash()` accepts a `FATAL EXCEPTION` from **any** process. That is the tool's success signal, so it is kept. The harness records which process crashed, and the audit counts only crashes in the app under test. In the earlier run, a crash of the UI-test runner was counted as reproducing a Gallery bug.

## Shared settings (both tools)

- **Model.** Gemini 2.5 Pro on Vertex AI, with messages converted exactly as CARBON's `carbon/my_gpt.py` does: a system turn becomes `[System]: …` plus `Understood.`. Thinking is left at the model default, as it was for CARBON and ReBL.
- **Device preparation.** This is CARBON's `carbon/run_dataset.py`:
  - uninstall, then install with `adb install -r -d -t`, with no auto-granted permissions;
  - launcher apps are set as the default home screen;
  - launch;
  - the same seed media.

  ReActDroid is the exception: its own `install_app` uses `adb install -g`, which pre-grants runtime permissions, so the harness installs it with `-g` too. The harness also allows "All files access" (`appops set <pkg> MANAGE_EXTERNAL_STORAGE allow`), a special permission `-g` does not cover. Without these, runs spent their whole 30 minutes on Android's permission dialog or the "All files access" Settings page, which ReActDroid cannot operate. This gives the baseline the easier start its authors intended.
- **Launcher apps** are made the default home screen using the activity the package manager resolves for HOME. CARBON's `run_dataset.py` fell back to `<package>/.LawnchairLauncher`, which is right only for Lawnchair itself. If the home screen does not come up, the app is started directly. `run.json` records the app in the foreground when the tool starts.
- **Budget.** 1,800 s of wall-clock time per run, the paper's budget.
- **Evidence.** Logcat from all buffers with process IDs, a screen recording, a final screenshot, the tool's own logs, and a per-call token log.
