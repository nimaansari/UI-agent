#!/usr/bin/env python3
# test_vnc_v1_chrome_visible.py
# TEST NAME: V.1 - Chrome Opens on Real Desktop
# WHAT USER SEES: Chrome window opens on desktop

import time, os, subprocess, hashlib, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chrome_session_display0 import get_ctrl, reset

print("=" * 55)
print("TEST V.1 - Chrome Opens Visibly on Desktop")
print("=" * 55)
print("WATCH YOUR DESKTOP — Chrome should open in 3 seconds")

# Screenshot desktop BEFORE Chrome opens
env = {**os.environ, "DISPLAY": ":0"}
subprocess.run(["scrot", "-o", "/tmp/v1_before_desktop.png"], env=env, capture_output=True)
size_before = os.path.getsize("/tmp/v1_before_desktop.png")
hash_before = ""
with open("/tmp/v1_before_desktop.png", "rb") as f:
 hash_before = hashlib.md5(f.read()).hexdigest()

print(f"\n BEFORE desktop screenshot : {size_before:,} bytes")
print(f" BEFORE hash : {hash_before}")

# Launch Chrome on :0
ctrl = get_ctrl()
reset("https://example.com", wait=3)
time.sleep(2)

# Screenshot desktop AFTER Chrome opens
subprocess.run(["scrot", "-o", "/tmp/v1_after_desktop.png"], env=env, capture_output=True)
size_after = os.path.getsize("/tmp/v1_after_desktop.png")
with open("/tmp/v1_after_desktop.png", "rb") as f:
 hash_after = hashlib.md5(f.read()).hexdigest()

title = ctrl.js("document.title") or ""
url = ctrl.js("window.location.href") or ""

print(f"\n AFTER desktop screenshot : {size_after:,} bytes")
print(f" AFTER hash : {hash_after}")
print(f" Chrome title : '{title}'")
print(f" Chrome URL : '{url}'")

# Assertions
assert size_before > 200000, f"FAIL V.1: Before screenshot too small ({size_before}b)"
assert size_after > 200000, f"FAIL V.1: After screenshot too small ({size_after}b)"
assert hash_before != hash_after, (
 f"FAIL V.1: Desktop did not change\n"
 f" before: {hash_before}\n"
 f" after: {hash_after}\n"
 f" → Chrome may not have opened on :0"
)
assert "example" in url.lower(), f"FAIL V.1: Wrong URL: {url}"
assert title, "FAIL V.1: No page title"

print(f"\n✅ V.1 PASSED — Chrome opened visibly on desktop")
print(f" Desktop changed: {hash_before[:16]} → {hash_after[:16]}")
print(f" Chrome showing: '{title}' at {url}")
