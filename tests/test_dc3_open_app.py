#!/usr/bin/env python3
# test_dc3_open_app.py
# Test: Open gedit and verify desktop changed

import sys
import os
import time
sys.path.insert(0, '/home/nimapro1381/.openclaw/workspace/gui-cowork/src')

from desktop_controller import DesktopController
import subprocess

print("=" * 60)
print("DC.3 Test — Open gedit and Verify Screen Changed")
print("=" * 60)

try:
    ctrl = DesktopController()

    print("\n[1] Taking BEFORE screenshot...")
    h_before = ctrl.screenshot_hash("/tmp/dc3_before.png")
    size_before = os.path.getsize("/tmp/dc3_before.png")
    print(f"✅ BEFORE hash: {h_before[:16]}...")
    print(f"✅ BEFORE size: {size_before:,} bytes")

    print("\n[2] Opening gedit...")
    proc = ctrl.open_app("gedit", wait=3)
    time.sleep(2)
    print(f"✅ gedit launched (PID {proc.pid})")

    print("\n[3] Taking AFTER screenshot...")
    h_after = ctrl.screenshot_hash("/tmp/dc3_after.png")
    size_after = os.path.getsize("/tmp/dc3_after.png")
    print(f"✅ AFTER hash: {h_after[:16]}...")
    print(f"✅ AFTER size: {size_after:,} bytes")

    print("\n[4] Verifying change...")
    changed = h_before != h_after
    print(f"✅ Changed: {changed}")

    assert changed, (
        f"FAIL DC.3: Desktop unchanged after opening gedit\n"
        f"  BEFORE hash: {h_before}\n"
        f"  AFTER hash: {h_after}"
    )

    print("\n[5] Cleaning up...")
    subprocess.run(["pkill", "gedit"], stderr=subprocess.DEVNULL)
    time.sleep(1)
    print("✅ gedit closed")

    print("\n" + "=" * 60)
    print("✅ DC.3 PASSED — gedit opened, desktop changed")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ DC.3 FAILED: {e}")
    subprocess.run(["pkill", "gedit"], stderr=subprocess.DEVNULL)
    import traceback
    traceback.print_exc()
    sys.exit(1)
