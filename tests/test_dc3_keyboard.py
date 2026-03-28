#!/usr/bin/env python3
# test_dc3_keyboard.py
# Proves ydotool types into real apps

import os, hashlib, subprocess, time

print("=" * 55)
print("TEST DC.3 — Keyboard Input via ydotool")
print("=" * 55)

OUTPUT = "/tmp/dc3_keyboard_test.txt"
if os.path.exists(OUTPUT):
    os.remove(OUTPUT)

def screenshot_hash(path="/tmp/dc3_hash.png"):
    subprocess.run(["gnome-screenshot", "-f", path], capture_output=True)
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# Open terminal (try xterm first, fall back to gnome-terminal)
print("\n Opening terminal...")
import shutil

if shutil.which("xterm"):
    print(" Using xterm")
    proc = subprocess.Popen(
        ["xterm"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2.5)
elif shutil.which("gnome-terminal"):
    print(" Using gnome-terminal")
    proc = subprocess.Popen(
        ["gnome-terminal", "--", "bash"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)
else:
    print(" ❌ No terminal found (xterm or gnome-terminal)")
    raise RuntimeError("No terminal available for test")

h_before = screenshot_hash("/tmp/dc3_before.png")
print(f" BEFORE hash : {h_before}")

# Type command via ydotool
cmd = f"echo 'UIAgent keyboard test' > {OUTPUT}"
print(f"\n Typing: {cmd}")
subprocess.run(["ydotool", "type", "--key-delay=50", "--", cmd], capture_output=True)
time.sleep(0.3)

# Press Enter
subprocess.run(["ydotool", "key", "--", "enter"], capture_output=True)
time.sleep(1.5)

h_after = screenshot_hash("/tmp/dc3_after.png")
exists = os.path.exists(OUTPUT)
content = open(OUTPUT).read().strip() if exists else ""

print(f" AFTER hash : {h_after}")
print(f" Hash changed : {h_before != h_after}")
print(f" File exists : {exists}")
print(f" File content : '{content}'")

subprocess.run(["pkill", "xterm"], capture_output=True)
subprocess.run(["pkill", "gnome-terminal"], capture_output=True)

assert exists, (
    f"FAIL DC.3: Output file not created\n"
    f" → ydotool may not be typing into the terminal\n"
    f" → Check /dev/uinput: ls -la /dev/uinput"
)
assert "UIAgent keyboard test" in content, (
    f"FAIL DC.3: Wrong content: '{content}'"
)
print(f" ✅ File content verified: '{content}'")

print(f"\n✅ DC.3 PASSED — keyboard input verified by file content")
