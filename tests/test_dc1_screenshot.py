#!/usr/bin/env python3
# test_dc1_screenshot.py
# Test: Screenshot real desktop via gnome-screenshot

import sys
import os
sys.path.insert(0, '/home/nimapro1381/.openclaw/workspace/gui-cowork/src')

from desktop_controller import DesktopController

print("=" * 60)
print("DC.1 Test — Screenshot Real Desktop")
print("=" * 60)

try:
    ctrl = DesktopController()

    print("\n[1] Taking screenshot...")
    path = ctrl.screenshot("/tmp/dc1_test.png")
    size = os.path.getsize(path)
    print(f"✅ Screenshot: {path}")
    print(f"✅ Size: {size:,} bytes")

    print("\n[2] Computing hash...")
    hash1 = ctrl.screenshot_hash("/tmp/dc1_hash.png")
    print(f"✅ Hash: {hash1}")

    print("\n[3] Verifying size...")
    assert size > 100000, f"FAIL: screenshot {size}b too small"
    print(f"✅ Size verified: {size:,}b > 100KB")

    print("\n[4] Verifying hash...")
    assert hash1, "FAIL: no hash"
    assert len(hash1) == 32, f"FAIL: hash wrong length {len(hash1)}"
    print(f"✅ Hash verified: {hash1[:16]}...")

    print("\n" + "=" * 60)
    print("✅ DC.1 PASSED — Real desktop screenshot verified")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ DC.1 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
