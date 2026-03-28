#!/usr/bin/env python3
"""
desktop_controller.py

Controls the real GNOME desktop from OpenClaw service context.
No display needed. No VNC. No RDP.

Uses:
 gnome-screenshot → screenshots of real desktop (:0)
 pyatspi → mouse clicks and keyboard on real desktop (:0)

Usage:
 from desktop_controller import DesktopController

 ctrl = DesktopController()

 # Screenshot
 path = ctrl.screenshot() # saves to /tmp/desktop.png
 b64 = ctrl.screenshot_base64() # base64 PNG string
 hash = ctrl.screenshot_hash() # MD5 hash for change detection

 # Mouse
 ctrl.click(960, 540) # left click
 ctrl.double_click(960, 540) # double click
 ctrl.right_click(960, 540) # right click
 ctrl.mouse_move(960, 540) # move (cosmetic only)

 # Keyboard
 ctrl.type_text("hello world") # type text
 ctrl.key("Return") # press key
 ctrl.key("ctrl+s") # key combo

 # Apps
 ctrl.open_app("gedit") # open any app
 ctrl.open_app("google-chrome", "https://google.com")

 # Verification
 h1 = ctrl.screenshot_hash()
 ctrl.click(100, 100)
 h2 = ctrl.screenshot_hash()
 changed = h1 != h2 # True if screen changed
"""

import os
import time
import base64
import hashlib
import subprocess

import pyatspi


# ── Key mappings ───────────────────────────────────────────────────────────

KEYSYM = {
    "Return": 0xff0d,
    "Tab": 0xff09,
    "Escape": 0xff1b,
    "BackSpace": 0xff08,
    "Delete": 0xffff,
    "Home": 0xff50,
    "End": 0xff57,
    "Left": 0xff51,
    "Right": 0xff53,
    "Up": 0xff52,
    "Down": 0xff54,
    "F1": 0xffbe,
    "F2": 0xffbf,
    "F4": 0xffc1,
    "F5": 0xffc2,
    "F11": 0xffc8,
    "ctrl": 0xffe3,
    "shift": 0xffe1,
    "alt": 0xffe9,
    "super": 0xffeb,
}


class DesktopController:
    """
    Controls the real GNOME desktop from a headless service context.
    Works on Wayland + VirtualBox without any display access.
    """

    def __init__(self, screenshot_path="/tmp/desktop_screenshot.png"):
        self.default_screenshot = screenshot_path
        self._verify_setup()

    def _verify_setup(self):
        """Verify both tools are available."""
        import shutil

        if not shutil.which("gnome-screenshot"):
            raise RuntimeError(
                "gnome-screenshot not found\n"
                "Install: sudo apt-get install gnome-screenshot"
            )

        try:
            import pyatspi
        except ImportError:
            raise RuntimeError(
                "pyatspi not found\n"
                "Install: sudo apt-get install python3-pyatspi"
            )

        print("[desktop] ✅ gnome-screenshot + pyatspi ready")

    # ── Screenshots ────────────────────────────────────────────────────────

    def screenshot(self, path=None):
        """
        Take screenshot of real desktop.
        Returns path to saved PNG file.
        """
        path = path or self.default_screenshot

        result = subprocess.run(
            ["gnome-screenshot", "-f", path],
            capture_output=True
        )

        if result.returncode != 0 or not os.path.exists(path):
            raise RuntimeError(
                f"gnome-screenshot failed\n"
                f"stderr: {result.stderr.decode()[:100]}"
            )

        size = os.path.getsize(path)
        if size < 10000:
            raise RuntimeError(
                f"Screenshot too small ({size}b) — not real desktop\n"
                f"Make sure you are logged into a GNOME session"
            )

        print(f"[desktop] screenshot: {path} ({size:,} bytes)")
        return path

    def screenshot_base64(self, path=None):
        """Take screenshot and return as base64 PNG string."""
        path = self.screenshot(path)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def screenshot_hash(self, path=None):
        """Take screenshot and return MD5 hash."""
        path = self.screenshot(path or "/tmp/desktop_hash.png")
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def screen_changed(self, hash_before, settle=1.2):
        """Check if screen changed since hash_before was taken."""
        time.sleep(settle)
        hash_after = self.screenshot_hash()
        changed = hash_before != hash_after
        if not changed:
            print("[desktop] ⚠️ screen unchanged")
        return changed, hash_after

    # ── Mouse ──────────────────────────────────────────────────────────────

    def click(self, x, y):
        """Left click at (x, y) on real desktop."""
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

    def mouse_move(self, x, y):
        """Move mouse to (x, y). Note: cursor may not visibly move."""
        pyatspi.Registry.generateMouseEvent(x, y, "abs")
        time.sleep(0.05)

    def scroll_down(self, x, y, clicks=3):
        """Scroll down at (x, y)."""
        for _ in range(clicks):
            pyatspi.Registry.generateMouseEvent(x, y, "b5c")
            time.sleep(0.05)
        print(f"[desktop] scroll_down x{clicks} at ({x}, {y})")

    def scroll_up(self, x, y, clicks=3):
        """Scroll up at (x, y)."""
        for _ in range(clicks):
            pyatspi.Registry.generateMouseEvent(x, y, "b4c")
            time.sleep(0.05)
        print(f"[desktop] scroll_up x{clicks} at ({x}, {y})")

    # ── Keyboard ───────────────────────────────────────────────────────────

    def type_text(self, text, delay=0.04):
        """Type text character by character."""
        for char in text:
            pyatspi.Registry.generateKeyboardEvent(
                0, char, pyatspi.KEY_STRING
            )
            time.sleep(delay)
        print(f"[desktop] typed: '{text[:50]}'")

    def key(self, combo):
        """
        Press a key or key combination.

        Examples:
         ctrl.key("Return")
         ctrl.key("Tab")
         ctrl.key("ctrl+s")
         ctrl.key("ctrl+c")
         ctrl.key("alt+F4")
         ctrl.key("ctrl+shift+n")
        """
        parts = combo.lower().split("+")

        # Single key
        if len(parts) == 1:
            k = combo
            if k in KEYSYM:
                pyatspi.Registry.generateKeyboardEvent(
                    KEYSYM[k], None, pyatspi.KEY_PRESSRELEASE
                )
            else:
                pyatspi.Registry.generateKeyboardEvent(
                    0, k, pyatspi.KEY_STRING
                )

        # Key combo (e.g. ctrl+s)
        else:
            modifiers = parts[:-1]
            main_key = parts[-1]

            # Press modifiers
            for mod in modifiers:
                if mod in KEYSYM:
                    pyatspi.Registry.generateKeyboardEvent(
                        KEYSYM[mod], None, pyatspi.KEY_PRESS
                    )
                    time.sleep(0.02)

            # Press main key
            if main_key in KEYSYM:
                pyatspi.Registry.generateKeyboardEvent(
                    KEYSYM[main_key], None, pyatspi.KEY_PRESSRELEASE
                )
            else:
                pyatspi.Registry.generateKeyboardEvent(
                    0, main_key, pyatspi.KEY_STRING
                )
            time.sleep(0.02)

            # Release modifiers (reverse order)
            for mod in reversed(modifiers):
                if mod in KEYSYM:
                    pyatspi.Registry.generateKeyboardEvent(
                        KEYSYM[mod], None, pyatspi.KEY_RELEASE
                    )
                    time.sleep(0.02)

        print(f"[desktop] key: {combo}")

    # ── App launching ──────────────────────────────────────────────────────

    def open_app(self, app, *args, wait=2.0):
        """
        Launch a desktop application.
        App opens on real desktop and is visible to user.

        Examples:
         ctrl.open_app("gedit")
         ctrl.open_app("nautilus", "/home/user/Documents")
         ctrl.open_app("google-chrome", "https://google.com")
        """
        import shutil

        binary = shutil.which(app)
        if not binary:
            raise RuntimeError(f"App not found: {app}")

        # Launch with Wayland environment
        env = {**os.environ}
        env.pop("WAYLAND_DISPLAY", None)  # let app auto-detect

        cmd = [binary] + list(args)
        proc = subprocess.Popen(
            cmd, env=env,
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

    def open_run_dialog(self):
        """Open GNOME run dialog with Alt+F2."""
        pyatspi.Registry.generateKeyboardEvent(
            KEYSYM["alt"], None, pyatspi.KEY_PRESS
        )
        time.sleep(0.05)
        pyatspi.Registry.generateKeyboardEvent(
            KEYSYM["F2"], None, pyatspi.KEY_PRESSRELEASE
        )
        time.sleep(0.05)
        pyatspi.Registry.generateKeyboardEvent(
            KEYSYM["alt"], None, pyatspi.KEY_RELEASE
        )
        time.sleep(0.8)
        print("[desktop] run dialog opened")

    # ── Verification ───────────────────────────────────────────────────────

    def wait_for_change(self, timeout=10, interval=0.5):
        """
        Wait until desktop changes.
        Returns True if changed, False if timeout.
        """
        hash_before = self.screenshot_hash()
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(interval)
            if self.screenshot_hash() != hash_before:
                print(f"[desktop] ✅ desktop changed")
                return True
        print(f"[desktop] ⚠️ desktop unchanged after {timeout}s")
        return False
