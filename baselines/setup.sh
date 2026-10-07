#!/usr/bin/env bash
# One-time setup for the AdbGPT / ReActDroid retest. Creates two Python 3.10
# virtualenvs and installs the Appium UiAutomator2 driver. It does not install
# system software; it tells you what is missing.
set -uo pipefail
cd "$(dirname "$0")"

missing=0
need() { printf '  %-28s' "$1"; if eval "$2" >/dev/null 2>&1; then echo ok; else echo "MISSING -> $3"; missing=1; fi; }

echo "System prerequisites:"
need "python3.10" "command -v python3.10" "brew install python@3.10"
need "Android SDK (ANDROID_HOME)" "test -x \"\${ANDROID_HOME:-$HOME/Library/Android/sdk}/platform-tools/adb\"" \
     "install Android Studio or: brew install --cask android-commandlinetools; then sdkmanager 'platform-tools' 'emulator' 'system-images;android-34;google_apis;arm64-v8a'"
need "Java (for Appium)" "/usr/libexec/java_home" "brew install --cask temurin@17"
need "node + appium" "command -v appium" "npm install -g appium"
if [ "$missing" = 1 ]; then
  echo "Install the missing items above, then re-run ./setup.sh"
  exit 1
fi

export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
make_venv() {  # name requirements
  local venv=".venv-$1" req="$2"
  echo "Creating $venv ..."
  python3.10 -m venv "$venv"
  "$venv/bin/pip" install -q --upgrade pip
  if ! "$venv/bin/pip" install -q -r "$req"; then
    # Some 2022-era pins have no wheel for this Mac; fall back to unpinned
    # versions for those and record exactly what was installed.
    echo "  pinned install failed; retrying without version pins"
    sed -E 's/[=<>]=?[^#;]*//' "$req" | "$venv/bin/pip" install -q -r /dev/stdin || return 1
  fi
  "$venv/bin/pip" freeze > "$venv.freeze.txt"
  echo "  installed versions recorded in $venv.freeze.txt"
}
make_venv adbgpt requirements-adbgpt.txt || exit 1
make_venv reactdroid requirements-reactdroid.txt || exit 1

echo "Appium UiAutomator2 driver ..."
appium driver list --installed 2>&1 | grep -q uiautomator2 || appium driver install uiautomator2

cat <<'EOF'

Setup done. Next:
  1. Put the benchmark APKs in each case folder, or pass --apk-root <folder>.
  2. Make sure ../.env has LLM_PROVIDER=vertex and LLM_API_KEY (same as CARBON).
  3. Start the emulator, then:  python3 ../carbon/push_seed_media.py 5554
  4. ReActDroid only, in another terminal:  appium --base-path /wd/hub
  5. .venv-adbgpt/bin/python harness/preflight.py --tool adbgpt --llm
See README.md for the pilot and the full run.
EOF
