"""adb helpers for the baseline harness.

Device preparation copies CARBON's carbon/run_dataset.py::install_and_launch
and cleanup_app so every tool starts each case from the same state: uninstall
any old copy, install the case APK without auto-granting permissions, make a
launcher app the default home screen, then launch the app.
"""
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

STOCK_LAUNCHER = "com.google.android.apps.nexuslauncher/.NexusLauncherActivity"


def find_adb():
    """Locate a real adb binary. The previous AdbGPT run failed because its
    `sh -c adb ...` calls could not find adb on PATH; the harness prepends this
    binary's folder to the PATH of every tool process."""
    candidates = [os.environ.get("ADB", "")]
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(var):
            candidates.append(os.path.join(os.environ[var], "platform-tools", "adb"))
    candidates.append(os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"))
    candidates.append(shutil.which("adb") or "")
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return os.path.realpath(c)
    try:
        import adbutils
        return adbutils.adb_path()
    except Exception:
        return None


def child_env(adb_path, serial, extra=None):
    """Environment for a tool process: adb first on PATH, device selected by
    ANDROID_SERIAL (honoured by adb, uiautomator2 and the patched ReActDroid)."""
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(adb_path) + os.pathsep + env.get("PATH", "")
    env["ANDROID_SERIAL"] = serial
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    if extra:
        env.update({k: str(v) for k, v in extra.items()})
    return env


class Device:
    def __init__(self, serial, adb_path=None):
        self.serial = serial
        self.adb_path = adb_path or find_adb()
        if not self.adb_path:
            raise RuntimeError("adb not found: install Android platform-tools or set ADB / ANDROID_HOME")

    def adb(self, *args, timeout=120, check=False):
        return subprocess.run([self.adb_path, "-s", self.serial, *args], capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout, check=check)

    def shell(self, cmd, timeout=60):
        return self.adb("shell", cmd, timeout=timeout).stdout

    # ---- device facts -----------------------------------------------------
    def state(self):
        return self.adb("get-state", timeout=15).stdout.strip()

    def api_level(self):
        return self.shell("getprop ro.build.version.sdk").strip()

    def android_version(self):
        return self.shell("getprop ro.build.version.release").strip()

    def screen_size(self):
        out = self.shell("wm size")
        sizes = dict(re.findall(r"(Physical|Override) size: (\d+x\d+)", out))
        w, h = (sizes.get("Override") or sizes.get("Physical", "0x0")).split("x")
        return int(w), int(h)

    def has_package(self, package):
        return f"package:{package}" in self.shell(f"pm list packages {package}").split()

    def version_name(self, package):
        m = re.search(r"versionName=(\S+)", self.shell(f"dumpsys package {package}"))
        return m.group(1) if m else None

    def launch_activity(self, package):
        """Launcher activity as reported by the package manager, e.g. .MainActivity."""
        out = self.shell(f"cmd package resolve-activity --brief -c android.intent.category.LAUNCHER {package}")
        for line in reversed(out.strip().splitlines()):
            if line.startswith(package + "/"):
                act = line.split("/", 1)[1].strip()
                return act[len(package):] if act.startswith(package + ".") else act
        return None

    def home_component(self, package):
        """The package's HOME activity as package/class, or None. (CARBON's
        run_dataset.py looked for a "package/" token in query-activities output,
        which API 34 never prints, and fell back to <package>/.LawnchairLauncher:
        right only for Lawnchair itself.)"""
        out = self.shell("cmd package resolve-activity --brief -a android.intent.action.MAIN "
                         f"-c android.intent.category.HOME {package}")
        for line in reversed(out.strip().splitlines()):
            if line.strip().startswith(package + "/"):
                return line.strip()
        out = self.shell("cmd package query-activities -a android.intent.action.MAIN "
                         f"-c android.intent.category.HOME {package}")
        names = re.findall(r"^\s*name=(\S+)", out, re.M)
        return f"{package}/{names[0]}" if names else None

    def foreground_package(self):
        out = self.shell("dumpsys activity activities")
        m = re.search(r"(?:topResumedActivity|mResumedActivity|ResumedActivity)[:=]\s*ActivityRecord\{\S+ \S+ ([\w.]+)/", out)
        return m.group(1) if m else None

    def is_launcher_app(self, package):
        out = self.shell("cmd package query-activities -a android.intent.action.MAIN "
                         f"-c android.intent.category.HOME {package}")
        return package in (out or "")

    # ---- per-case preparation (same as CARBON's run_dataset.py) ------------
    def install_and_launch(self, apk_path, package, log, grant_runtime_permissions=False):
        """grant_runtime_permissions adds `-g`, as ReActDroid's own install_app does,
        and also allows "All files access" (MANAGE_EXTERNAL_STORAGE), a special
        permission `-g` does not cover. Apps that ask for it open a Settings page
        on first launch, which ReActDroid cannot operate."""
        flags = ["-r", "-d", "-t"] + (["-g"] if grant_runtime_permissions else [])
        log(f"installing {Path(apk_path).name} ({package}) with adb install {' '.join(flags)}")
        self.adb("uninstall", package, timeout=120)
        res = self.adb("install", *flags, str(apk_path), timeout=300)
        if "INSTALL_FAILED_DEPRECATED_SDK_VERSION" in res.stdout + res.stderr:
            # Android 14 refuses apps that target SDK < 23 (e.g. ReBL's Memento APK)
            # unless this flag is given; the app itself is unchanged.
            flags.append("--bypass-low-target-sdk-block")
            log(f"target SDK below 23: retrying with adb install {' '.join(flags)}")
            res = self.adb("install", *flags, str(apk_path), timeout=300)
        if "Success" not in res.stdout:
            raise RuntimeError(f"install failed: {(res.stdout + res.stderr).strip()[-400:]}")
        time.sleep(2)
        if grant_runtime_permissions:
            self.shell(f"appops set {package} MANAGE_EXTERNAL_STORAGE allow")
        was_launcher = self.is_launcher_app(package)
        comp = self.home_component(package) if was_launcher else None
        if comp:
            self.shell(f"cmd package set-home-activity {comp}")
            log(f"set default launcher -> {comp}")
            time.sleep(1)
            self.shell("input keyevent KEYCODE_HOME")
        else:
            if was_launcher:
                log("could not resolve the HOME activity; launching the app directly")
            self.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        time.sleep(2)
        if self.foreground_package() != package:
            # e.g. a launcher whose home screen did not come up: start the app itself
            log(f"foreground is {self.foreground_package()}, not {package}; launching the app")
            self.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            time.sleep(2)
        return was_launcher

    def focused_window(self):
        m = re.search(r"mCurrentFocus=(.*)", self.shell("dumpsys window") or "")
        return m.group(1).strip() if m else None

    def foreign_anr_dialogs(self, package):
        """Processes other than `package` whose "isn't responding" dialog is open."""
        out = self.shell("dumpsys window windows")
        return sorted({p for p in re.findall(r"Application Not Responding: ([\w.:]+)", out or "", re.I)
                       if p.split(":")[0] != package})

    def close_foreign_anr_dialogs(self, package, was_launcher, log):
        """On a freshly booted CI emulator the system launcher can stop
        responding during boot and install, leaving its "isn't responding"
        dialog over the app under test before the tool starts (24 of the first
        100 AdbGPT runs). Killing the unresponsive process closes its dialog,
        then the app is brought back to the front. A dialog of the app under
        test itself is left alone: that is part of the run. Returns the
        processes whose dialog was closed."""
        closed = []
        for _ in range(3):
            pkgs = self.foreign_anr_dialogs(package)
            if not pkgs:
                break
            for proc in pkgs:
                log(f"closing the 'isn't responding' dialog of {proc} (force-stop) before the tool starts")
                self.shell(f"am force-stop {proc.split(':')[0]}")
                closed.append(proc)
            time.sleep(3)
        if closed and self.foreground_package() != package:
            self.shell("input keyevent KEYCODE_HOME" if was_launcher
                       else f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
            time.sleep(2)
        return closed

    def cleanup(self, package, was_launcher, log):
        try:
            if was_launcher:
                self.shell(f"cmd package set-home-activity {STOCK_LAUNCHER}")
                self.shell("input keyevent KEYCODE_HOME")
                time.sleep(1)
            self.shell(f"am force-stop {package}")
            self.adb("uninstall", package, timeout=120)
        except Exception as e:
            log(f"cleanup warning: {e}")

    # ---- evidence ----------------------------------------------------------
    def screenshot(self, path):
        with open(path, "wb") as f:
            subprocess.run([self.adb_path, "-s", self.serial, "exec-out", "screencap", "-p"],
                           stdout=f, stderr=subprocess.DEVNULL, timeout=30)

    def start_logcat(self, path):
        """Clear all buffers, then stream main/system/crash with timestamps and
        PIDs so a crash can be attributed to the app's own process."""
        self.adb("logcat", "-b", "all", "-c", timeout=30)
        f = open(path, "w", encoding="utf-8", errors="replace")
        proc = subprocess.Popen([self.adb_path, "-s", self.serial, "logcat", "-b", "main,system,crash",
                                 "-v", "threadtime"], stdout=f, stderr=subprocess.STDOUT)
        return proc, f


class ScreenRecorder:
    """Records the screen in back-to-back 170 s segments (Android's screenrecord
    stops at 180 s) and pulls them when stopped."""

    def __init__(self, device, out_dir):
        self.device, self.out_dir = device, Path(out_dir)
        self._stop = threading.Event()
        self._thread = None
        self.segments = []

    def _loop(self):
        i = 0
        while not self._stop.is_set():
            remote = f"/sdcard/carbon_retest_rec_{i:02d}.mp4"
            self.segments.append(remote)
            proc = subprocess.Popen([self.device.adb_path, "-s", self.device.serial, "shell",
                                     "screenrecord", "--time-limit", "170", remote],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            while proc.poll() is None and not self._stop.is_set():
                time.sleep(0.5)
            if proc.poll() is None:
                self.device.shell("pkill -INT screenrecord")
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
            i += 1

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=30)
        time.sleep(1)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        pulled = []
        for remote in self.segments:
            local = self.out_dir / Path(remote).name
            self.device.adb("pull", remote, str(local), timeout=120)
            self.device.shell(f"rm -f {remote}")
            if local.exists() and local.stat().st_size > 0:
                pulled.append(local.name)
        return pulled


_FATAL = re.compile(r"E AndroidRuntime: FATAL EXCEPTION: (.*)")
_PROCESS = re.compile(r"E AndroidRuntime: Process: ([\w.:]+), PID: (\d+)")
_ANR = re.compile(r"ANR in ([\w.:]+)")


def parse_crashes(logcat_text, package):
    """Crashes and ANRs in a logcat capture, each tagged with its process, so the
    audit can tell an app crash from a crash in another process (the previous
    ReActDroid run counted an instrumentation-runner crash as a success)."""
    events = []
    lines = logcat_text.splitlines()
    for i, line in enumerate(lines):
        m = _FATAL.search(line)
        if m:
            proc = None
            exception = None
            for nxt in lines[i + 1:i + 6]:
                if _FATAL.search(nxt):
                    break  # next crash block; its Process line is not ours
                pm = _PROCESS.search(nxt)
                if pm and proc is None:
                    proc = pm.group(1)
                elif proc and "AndroidRuntime" in nxt and exception is None:
                    exception = nxt.split("AndroidRuntime:", 1)[1].strip()
            events.append({"kind": "crash", "thread": m.group(1).strip(), "process": proc,
                           "exception": exception, "line": line.strip()[:300]})
            continue
        m = _ANR.search(line)
        if m:
            events.append({"kind": "anr", "process": m.group(1), "line": line.strip()[:300]})
    in_app = [e for e in events if e.get("process") and e["process"].split(":")[0] == package]
    return {"events": events, "app_crash_or_anr": bool(in_app), "app_events": in_app}
