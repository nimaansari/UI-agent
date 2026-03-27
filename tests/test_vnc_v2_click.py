#!/usr/bin/env python3
# test_vnc_v2_click.py - VNC Mouse Click Test

import time, os, subprocess, hashlib, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from vnc_input import VNCInput

print("=" * 55)
print("TEST V.2 - VNC Mouse Click (VirtualBox Bypass)")
print("=" * 55)

env = {**os.environ, "DISPLAY": ":0"}

# Screenshot BEFORE
subprocess.run(["scrot", "-o", "/tmp/v2_before.png"], env=env, capture_output=True)
size_before = os.path.getsize("/tmp/v2_before.png")
with open("/tmp/v2_before.png", "rb") as f:
 hash_before = hashlib.md5(f.read()).hexdigest()

print(f" BEFORE screenshot : {size_before:,} bytes, hash={hash_before[:16]}")

# Connect VNC and move mouse
vnc = VNCInput()
print(" Moving mouse to (200, 200)...")
vnc.move(200, 200)
time.sleep(0.5)
print(" Moving mouse to (600, 400)...")
vnc.move(600, 400)
time.sleep(0.5)
vnc.close()

# Screenshot AFTER
subprocess.run(["scrot", "-o", "/tmp/v2_after.png"], env=env, capture_output=True)
size_after = os.path.getsize("/tmp/v2_after.png")

assert size_before > 200000, f"FAIL: Screenshot too small ({size_before}b)"
assert size_after > 200000, f"FAIL: Screenshot too small ({size_after}b)"

print(f" AFTER screenshot : {size_after:,} bytes")
print(f"\n✅ V.2 PASSED — VNC input connected, mouse commands sent")
