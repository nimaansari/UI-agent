#!/usr/bin/env python3
# test_a3_xdotool_real.py
# TEST NAME: A.3 - xdotool Controls Real Desktop
# CRITICAL TEST: Mouse must actually move on physical desktop

import os, subprocess, time, sys

print("=" * 55)
print("TEST A.3 — xdotool Controls Real Desktop")
print("=" * 55)
print("\nWATCH YOUR DESKTOP — mouse cursor should move in 3 seconds")

# Initialize display
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from openclaw_display_init import init_display
    init_display()
except:
    pass

env = {**os.environ}

# Get mouse position BEFORE
r_before = subprocess.run(
    ["xdotool", "getmouselocation"],
    env=env, capture_output=True
)
assert r_before.returncode == 0, (
    f"FAIL A.3: xdotool getmouselocation failed\n"
    f" stderr: {r_before.stderr.decode()}"
)
pos_before = r_before.stdout.decode().strip()
print(f"\n BEFORE position : {pos_before}")

# Move mouse to a specific position
print(" Moving mouse to (300, 300)...")
subprocess.run(["xdotool", "mousemove", "300", "300"], env=env)
time.sleep(1)

# Move again to a clearly different position
print(" Moving mouse to (800, 500)...")
subprocess.run(["xdotool", "mousemove", "800", "500"], env=env)
time.sleep(1)

# Get position AFTER
r_after = subprocess.run(
    ["xdotool", "getmouselocation"],
    env=env, capture_output=True
)
pos_after = r_after.stdout.decode().strip()
print(f"\n AFTER position : {pos_after}")

# Extract X coordinates to compare
import re
x_before_match = re.search(r'x:(\d+)', pos_before)
x_after_match = re.search(r'x:(\d+)', pos_after)
x_before = int(x_before_match.group(1)) if x_before_match else 0
x_after = int(x_after_match.group(1)) if x_after_match else 0

print(f"\n X before : {x_before}")
print(f" X after : {x_after}")

assert x_before != x_after, (
    f"FAIL A.3: Mouse position did not change\n"
    f" before: {pos_before}\n"
    f" after: {pos_after}\n"
    f" X coordinate unchanged: {x_before}\n"
    f" → xdotool is NOT controlling the real desktop\n"
    f" → Make sure you are on X11 session (GNOME on Xorg)"
)
print(" ✅ Mouse position changed — xdotool controlling real desktop")

print(f"\n✅ A.3 PASSED — xdotool works on real desktop")
print(f" {pos_before} → {pos_after}")
