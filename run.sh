#!/bin/bash
# ======================================================================
#  CARBON — one-command runner
#
#  Usage:
#     ./run.sh <path-to-bug_report.txt>
#
#  Example:
#     ./run.sh "Dataset/double_tap/FossifyOrg_Gallery_847 Tested/bug_report.txt"
#
#  If no bug report is given, a sample bug is used.
#  Prerequisites:
#     1. Android SDK + an emulator (AVD).   Override with: AVD_NAME=MyAvd ./run.sh ...
#     2. cp .env.example .env  and add your LLM_API_KEY
#     3. pip install -r requirements.txt
# ======================================================================
set -e

ANDROID_SDK="${ANDROID_SDK:-$HOME/Library/Android/sdk}"
ADB="$ANDROID_SDK/platform-tools/adb"
EMULATOR="$ANDROID_SDK/emulator/emulator"
export PATH="$ANDROID_SDK/platform-tools:$ANDROID_SDK/emulator:$PATH"

TARGET_AVD="${AVD_NAME:-Pixel_4}"
BR_PATH="${1:-Dataset/double_tap/FossifyOrg_Gallery_847 Tested/bug_report.txt}"

if [ ! -f "$BR_PATH" ]; then
    echo "Error: bug report not found: $BR_PATH"
    echo "Usage: ./run.sh <path-to-bug_report.txt>"
    exit 1
fi

# ---- 1. ADB server ---------------------------------------------------
echo "[1/4] Starting ADB server..."
"$ADB" start-server >/dev/null 2>&1 || true

# ---- 2. Ensure an emulator is running --------------------------------
echo "[2/4] Checking for a running device..."
DEVICE_COUNT=$("$ADB" devices | grep -cE "device$|emulator" || true)

if [ "$DEVICE_COUNT" -eq 0 ]; then
    AVDS=$("$EMULATOR" -list-avds)
    if [ -z "$AVDS" ]; then
        echo "Error: no AVD found. Create one in Android Studio (Pixel 4, API 34 recommended)."
        exit 1
    fi
    if echo "$AVDS" | grep -qx "$TARGET_AVD"; then
        SELECTED_AVD="$TARGET_AVD"
    else
        SELECTED_AVD=$(echo "$AVDS" | head -n 1)
        echo "AVD '$TARGET_AVD' not found; using '$SELECTED_AVD'."
    fi
    echo "Starting emulator: $SELECTED_AVD"
    "$EMULATOR" -avd "$SELECTED_AVD" -no-snapshot-load >/dev/null 2>&1 &

    echo -n "Waiting for emulator to boot"
    WAITED=0
    while [ "$WAITED" -lt 120 ]; do
        DEVICE_COUNT=$("$ADB" devices | grep -cE "device$|emulator" || true)
        [ "$DEVICE_COUNT" -gt 0 ] && break
        sleep 3; WAITED=$((WAITED + 3)); echo -n "."
    done
    echo ""
    [ "$DEVICE_COUNT" -eq 0 ] && { echo "Error: emulator boot timed out."; exit 1; }
fi

DEVICE_SERIAL=$("$ADB" devices | grep -E "device$|emulator" | head -n 1 | awk '{print $1}')
DEVICE_PORT=$(echo "$DEVICE_SERIAL" | sed 's/emulator-//')
echo "Device: $DEVICE_SERIAL"

# ---- 3. Wait for full boot -------------------------------------------
echo "[3/4] Waiting for device to finish booting..."
"$ADB" -s "$DEVICE_SERIAL" wait-for-device
WAITED=0
while [ "$WAITED" -lt 60 ]; do
    [ "$("$ADB" -s "$DEVICE_SERIAL" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ] && break
    sleep 2; WAITED=$((WAITED + 2))
done

# ---- 4. Run CARBON ---------------------------------------------------
echo "[4/4] Running CARBON reproduction..."
cd "$(dirname "$0")/Automation"
[ -f ../env/bin/activate ] && source ../env/bin/activate

mkdir -p Results
BR_NAME=$(basename "$BR_PATH" .txt)
RUN_LOG="Results/${BR_NAME}_$(date +%Y%m%d_%H%M%S).log"

python3 -u reproduction.py "$DEVICE_PORT" "../$BR_PATH" 2>&1 | tee "$RUN_LOG"
