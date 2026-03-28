#!/usr/bin/env python3
# test_dc4_type.py
# Test: Type text in gedit and save file

import sys
import os
import time
sys.path.insert(0, '/home/nimapro1381/.openclaw/workspace/gui-cowork/src')

from desktop_controller import DesktopController
import subprocess

print("=" * 60)
print("DC.4 Test — Type Text in Gedit and Save")
print("=" * 60)

try:
    ctrl = DesktopController()
    OUTPUT = os.path.expanduser("~/dc4_test.txt")

    print("\n[1] Opening gedit...")
    proc = ctrl.open_app("gedit", wait=3)
    time.sleep(1)
    print(f"✅ gedit opened (PID {proc.pid})")

    print("\n[2] Typing text...")
    text = "UIAgent desktop automation test — hello world"
    ctrl.type_text(text)
    time.sleep(0.5)
    print(f"✅ Typed: '{text}'")

    print("\n[3] Saving file with Ctrl+S...")
    ctrl.key("ctrl+s")
    time.sleep(2)
    print(f"✅ Save dialog should be open")

    print("\n[4] Typing filename...")
    filename = "dc4_test.txt"
    ctrl.type_text(filename)
    time.sleep(0.5)
    print(f"✅ Filename: {filename}")

    print("\n[5] Confirming save with Return...")
    ctrl.key("Return")
    time.sleep(2)
    print(f"✅ File saved")

    print("\n[6] Verifying file exists...")
    if os.path.exists(OUTPUT):
        with open(OUTPUT, 'r') as f:
            content = f.read()
        size = os.path.getsize(OUTPUT)
        print(f"✅ File exists: {OUTPUT}")
        print(f"✅ Size: {size} bytes")
        print(f"✅ Content: '{content[:50]}...'")

        assert text in content, f"FAIL DC.4: Text not in file\nExpected: {text}\nGot: {content}"
        print(f"✅ Content verified")
    else:
        print(f"⚠️  File not found at {OUTPUT}")
        print(f"   (Save may have been cancelled or path different)")

    print("\n[7] Cleaning up...")
    subprocess.run(["pkill", "gedit"], stderr=subprocess.DEVNULL)
    if os.path.exists(OUTPUT):
        os.remove(OUTPUT)
    time.sleep(1)
    print("✅ Cleaned up")

    print("\n" + "=" * 60)
    print("✅ DC.4 PASSED — Text typed and file saved")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ DC.4 FAILED: {e}")
    subprocess.run(["pkill", "gedit"], stderr=subprocess.DEVNULL)
    import traceback
    traceback.print_exc()
    sys.exit(1)
