#!/usr/bin/env python3
# test_dc4_open_app.py
# Proves desktop apps open on real desktop from service context

import os, hashlib, subprocess, time

print("=" * 55)
print("TEST DC.4 — Open Desktop App")
print("=" * 55)

def screenshot_hash(path="/tmp/dc4_hash.png"):
    subprocess.run(["gnome-screenshot", "-f", path], capture_output=True)
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

h_before = screenshot_hash("/tmp/dc4_before.png")
size_before = os.path.getsize("/tmp/dc4_before.png")
print(f"\n BEFORE hash : {h_before}")
print(f" BEFORE size : {size_before:,} bytes")
print("\n Opening gedit...")
print(" WATCH YOUR DESKTOP — gedit should open")

proc = subprocess.Popen(
    ["gedit"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(3)

if proc.poll() is not None:
    print(" gedit not available — trying mousepad")
    proc = subprocess.Popen(
        ["mousepad"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)

h_after = screenshot_hash("/tmp/dc4_after.png")
size_after = os.path.getsize("/tmp/dc4_after.png")
running = proc.poll() is None

print(f"\n AFTER hash : {h_after}")
print(f" AFTER size : {size_after:,} bytes")
print(f" App running : {running} (PID {proc.pid})")
print(f" Hash changed: {h_before != h_after}")

assert running, "FAIL DC.4: App exited immediately"
assert h_before != h_after, (
    f"FAIL DC.4: Desktop unchanged after opening app\n"
    f" before: {h_before}\n after: {h_after}"
)

subprocess.run(["pkill", "gedit"], capture_output=True)
subprocess.run(["pkill", "mousepad"], capture_output=True)

print(f"\n✅ DC.4 PASSED — desktop app opened and verified")
print(f" Hash changed: {h_before[:16]} → {h_after[:16]}")
