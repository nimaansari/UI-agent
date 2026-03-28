#!/usr/bin/env python3
# test_dc1_screenshot.py
# Proves gnome-screenshot captures real desktop from service context

import os, hashlib, subprocess, time

print("=" * 55)
print("TEST DC.1 — Screenshot Real Desktop")
print("=" * 55)

def take_screenshot(path):
    r = subprocess.run(["gnome-screenshot", "-f", path], capture_output=True)
    return os.path.getsize(path) if os.path.exists(path) else 0

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# Take screenshot
size1 = take_screenshot("/tmp/dc1_shot1.png")
hash1 = file_hash("/tmp/dc1_shot1.png")
print(f"\n Screenshot 1 : {size1:,} bytes")
print(f" Hash 1 : {hash1}")

assert size1 > 100000, (
    f"FAIL DC.1: Screenshot too small ({size1}b)\n"
    f" → gnome-screenshot not capturing real desktop"
)
print(" ✅ Screenshot size verified (> 100KB)")

# Take second screenshot — should be same hash (nothing changed)
time.sleep(1)
size2 = take_screenshot("/tmp/dc1_shot2.png")
hash2 = file_hash("/tmp/dc1_shot2.png")
print(f"\n Screenshot 2 : {size2:,} bytes")
print(f" Hash 2 : {hash2}")
print(f" Same hash : {hash1 == hash2}")

assert size2 > 100000, "FAIL DC.1: Second screenshot too small"
print(" ✅ Both screenshots have real content")

print(f"\n✅ DC.1 PASSED — real desktop captured")
print(f" Size : {size1:,} bytes")
print(f" Hash : {hash1}")
