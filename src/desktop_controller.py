#!/usr/bin/env python3
"""
desktop_controller.py

Controls the real GNOME desktop from OpenClaw service context.
No display needed. Works on Wayland + VirtualBox.

Proven working:
  gnome-screenshot  screenshot: 394KB real desktop ✅
  pyatspi           mouse click: verified ✅
  ydotool           keyboard: types text into real apps ✅
"""

import os
import time
import base64
import hashlib
import subprocess
import pyatspi

KEYSYM = {
    "Return":    0xff0d,
    "Tab":       0xff09,
    "Escape":    0xff1b,
    "BackSpace": 0xff08,
    "Delete":    0xffff,
    "Home":      0xff50,
    "End":       0xff57,
    "Left":      0xff51,
    "Right":     0xff53,
    "Up":        0xff52,
    "Down":      0xff54,
    "F1":        0xffbe,
    "F2":        0xffbf,
    "F4":        0xffc1,
    "F5":        0xffc2,
    "F11":       0xffc8,
    "ctrl":      0xffe3,
    "shift":     0xffe1,
    "alt":       0xffe9,
    "super":     0xffeb,
}

KEY_MAP = {
    "Return":    "enter",
    "Tab":       "tab",
    "Escape":    "esc",
    "BackSpace": "backspace",
    "Delete":    "delete",
    "Home":      "home",
    "End":       "end",
    "Left":      "left",
    "Right":     "right",
    "Up":        "up",
    "Down":      "down",
    "ctrl":      "ctrl",
    "shift":     "shift",
    "alt":       "alt",
    "super":     "super",
    "F1": "f1", "F2": "f2", "F3": "f3", "F4": "f4",
    "F5": "f5", "F11": "f11",
}


class DesktopController:
    """
    Controls real GNOME desktop from headless service context.

    Usage:
        ctrl = DesktopController()
        ctrl.screenshot("/tmp/desktop.png")
        ctrl.click(960, 540)
        ctrl.type_text("hello world")
        ctrl.key("Return")
        ctrl.key("ctrl+s")
        ctrl.open_app("gedit")
    """

    def __init__(self):
        self._verify_setup()

    def _verify_setup(self):
        import shutil
        errors = []

        if not shutil.which("gnome-screenshot"):
            errors.append("gnome-screenshot missing: sudo apt-get install gnome-screenshot")

        if not shutil.which("ydotool"):
            errors.append("ydotool missing: sudo apt-get install ydotool")

        if not os.path.exists("/dev/uinput"):
            errors.append("/dev/uinput missing: sudo modprobe uinput && sudo chmod 666 /dev/uinput")

        if errors:
            raise RuntimeError("Setup issues:\n" + "\n".join(errors))

        print("[desktop] ✅ gnome-screenshot + pyatspi + ydotool ready")

    # ── Screenshots ────────────────────────────────────────────────────────

    def screenshot(self, path="/tmp/desktop.png"):
        """Screenshot real desktop. Returns path."""
        result = subprocess.run(
            ["gnome-screenshot", "-f", path],
            capture_output=True
        )
        if result.returncode != 0 or not os.path.exists(path):
            raise RuntimeError(
                f"gnome-screenshot failed: {result.stderr.decode()[:100]}"
            )
        size = os.path.getsize(path)
        print(f"[desktop] screenshot: {path} ({size:,} bytes)")
        return path

    def screenshot_base64(self, path="/tmp/desktop.png"):
        """Screenshot as base64 PNG string."""
        self.screenshot(path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def screenshot_hash(self, path="/tmp/desktop_hash.png"):
        """Screenshot as MD5 hash for change detection."""
        self.screenshot(path)
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def wait_for_change(self, timeout=10, interval=0.5):
        """Wait until desktop changes. Returns True if changed."""
        h_before = self.screenshot_hash()
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(interval)
            if self.screenshot_hash() != h_before:
                print("[desktop] ✅ screen changed")
                return True
        print(f"[desktop] ⚠️  no change after {timeout}s")
        return False

    # ── Mouse (pyatspi) ────────────────────────────────────────────────────

    def click(self, x, y):
        """Left click at (x, y)."""
        pyatspi.Registry.generateMouseEvent(x, y, "b1c")
        print(f"[desktop] click ({x}, {y})")
        time.sleep(0.1)

    def double_click(self, x, y):
        """Double click at (x, y)."""
        pyatspi.Registry.generateMouseEvent(x, y, "b1d")
        print(f"[desktop] double_click ({x}, {y})")
        time.sleep(0.1)

    def right_click(self, x, y):
        """Right click at (x, y)."""
        pyatspi.Registry.generateMouseEvent(x, y, "b3c")
        print(f"[desktop] right_click ({x}, {y})")
        time.sleep(0.1)

    def scroll_down(self, x, y, clicks=3):
        """Scroll down at (x, y)."""
        for _ in range(clicks):
            pyatspi.Registry.generateMouseEvent(x, y, "b5c")
            time.sleep(0.05)

    def scroll_up(self, x, y, clicks=3):
        """Scroll up at (x, y)."""
        for _ in range(clicks):
            pyatspi.Registry.generateMouseEvent(x, y, "b4c")
            time.sleep(0.05)

    # ── Keyboard (ydotool) ─────────────────────────────────────────────────

    def type_text(self, text, delay_ms=50):
        """
        Type text into focused app.
        Uses ydotool → /dev/uinput → bypasses Wayland security.
        """
        result = subprocess.run(
            ["ydotool", "type", f"--key-delay={delay_ms}", "--", text],
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ydotool type failed: {result.stderr.decode()[:100]}\n"
                f"Check: ls -la /dev/uinput"
            )
        print(f"[desktop] typed: '{text[:50]}'")

    def key(self, combo):
        """
        Press a key or combo.

        Examples:
            ctrl.key("Return")
            ctrl.key("Tab")
            ctrl.key("ctrl+s")
            ctrl.key("ctrl+shift+n")
            ctrl.key("alt+F4")
        """
        parts = combo.split("+")
        ydotool_parts = [KEY_MAP.get(p, p.lower()) for p in parts]
        key_str = "+".join(ydotool_parts)

        result = subprocess.run(
            ["ydotool", "key", "--", key_str],
            capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"ydotool key failed for '{combo}': "
                f"{result.stderr.decode()[:100]}"
            )
        print(f"[desktop] key: {combo}")
        time.sleep(0.1)

    # ── App launching ──────────────────────────────────────────────────────

    def open_app(self, app, *args, wait=2.5):
        """
        Launch a desktop app. Appears on real desktop.

        Examples:
            ctrl.open_app("gedit")
            ctrl.open_app("nautilus", "/home/user")
            ctrl.open_app("google-chrome", "https://google.com")
        """
        import shutil
        binary = shutil.which(app)
        if not binary:
            raise RuntimeError(f"App not found: {app}")

        proc = subprocess.Popen(
            [binary] + list(args),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(wait)

        if proc.poll() is not None:
            raise RuntimeError(
                f"{app} exited immediately (code {proc.returncode})"
            )

        print(f"[desktop] ✅ {app} launched (PID {proc.pid})")
        return proc

    def kill_app(self, name):
        """Kill app by name."""
        subprocess.run(["pkill", "-f", name], capture_output=True)
        time.sleep(0.5)
        print(f"[desktop] killed: {name}")
