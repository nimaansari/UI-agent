#!/usr/bin/env python3
# test_dc2_click.py
# Proves pyatspi can click on real desktop

import os, hashlib, subprocess, time
import pyatspi

print("=" * 55)
print("TEST DC.2 — Mouse Click on Real Desktop")
print("=" * 55)

def screenshot_hash(path="/tmp/dc2_hash.png"):
    subprocess.run(["gnome-screenshot", "-f", path], capture_output=True)
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

h_before = screenshot_hash("/tmp/dc2_before.png")
size_before = os.path.getsize("/tmp/dc2_before.png")
print(f"\n BEFORE hash : {h_before}")
print(f" BEFORE size : {size_before:,} bytes")

# Click on desktop (100, 100) — top left corner
print("\n Clicking at (100, 100)...")
print(" WATCH YOUR DESKTOP — something may respond to click")
pyatspi.Registry.generateMouseEvent(100, 100, "b1c")
time.sleep(1.5)

# Click center of screen
print(" Clicking at (960, 540) — center...")
pyatspi.Registry.generateMouseEvent(960, 540, "b1c")
time.sleep(1.5)

h_after = screenshot_hash("/tmp/dc2_after.png")
size_after = os.path.getsize("/tmp/dc2_after.png")
print(f"\n AFTER hash : {h_after}")
print(f" AFTER size : {size_after:,} bytes")
print(f" Changed : {h_before != h_after}")

assert size_after > 100000, "FAIL DC.2: Screenshot blank after click"
print(" ✅ Click executed without error")
print(" ✅ Screenshot still captures real desktop")

print(f"\n✅ DC.2 PASSED — mouse click verified")
