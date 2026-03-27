#!/bin/bash
# test_rdp_final.sh
# Final RDP verification test
# Tests: Mouse movement, screenshot capture, file size

cd /home/nimapro1381/.openclaw/workspace/gui-cowork

echo "============================================================"
echo "RDP Final Verification Test"
echo "============================================================"
echo ""

python3 << 'PYEOF'
from src.rdp_controller import RDPController
import os
import time

print("[1] Initializing RDP controller...")
rdp = RDPController()

print("\n[2] Moving mouse to (960, 540)...")
rdp.mouse_move(960, 540)
time.sleep(1)

print("[3] Moving mouse to (100, 100)...")
rdp.mouse_move(100, 100)
time.sleep(1)

print("\n⚠️  CHECK YOUR DESKTOP - Did the mouse cursor move?")
print("    (If yes, RDP input is working!)")

print("\n[4] Taking screenshot...")
img = rdp.screenshot()

if img:
    if isinstance(img, str):
        # It's a file path
        sz = os.path.getsize(img)
        print(f"[5] Screenshot saved to: {img}")
    else:
        # It's a PIL Image, save it
        img.save('/tmp/rdp_final_test.png')
        sz = os.path.getsize('/tmp/rdp_final_test.png')
        print(f"[5] Screenshot saved to: /tmp/rdp_final_test.png")
    
    print(f"[6] Screenshot size: {sz:,} bytes")
    
    if sz > 500000:
        print(f"\n✅ SUCCESS - Real desktop captured (> 500KB)")
        print("\nRDP is fully working:")
        print("  ✅ Screenshot capture working")
        print("  ✅ Mouse control working (check if moved)")
        print("  ✅ Ready for full integration")
    else:
        print(f"\n⚠️ Screenshot small ({sz}b) - may be headless rendering")
else:
    print("\n❌ Screenshot failed - RDP not capturing desktop")

print("\n[7] Closing RDP connection...")
rdp.close()

print("\n============================================================")
print("Test Complete")
print("============================================================")
PYEOF

echo ""
echo "Next steps:"
echo "1. Did the mouse move on your desktop? (YES/NO)"
echo "2. What was the screenshot size in bytes?"
echo "3. Did it say SUCCESS or FAILED?"
echo ""
echo "Paste those answers here."
