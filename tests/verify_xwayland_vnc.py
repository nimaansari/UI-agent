#!/usr/bin/env python3
# verify_xwayland_vnc.py — Verify x11vnc on Xwayland

import subprocess, socket, os, time, sys

print("=" * 60)
print("Xwayland + x11vnc Verification")
print("=" * 60)

results = {}

# 1. Find Xwayland
print("\n[1] Finding Xwayland display...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from find_xwayland import find_xwayland
    display, auth = find_xwayland()
    results["xwayland_found"] = bool(display and auth)
    if results["xwayland_found"]:
        print(f" ✅ display={display}, auth={os.path.basename(auth)}")
    else:
        print(f" ❌ Could not find Xwayland")
        display, auth = ":0", None
except Exception as e:
    results["xwayland_found"] = False
    print(f" ❌ {e}")
    display, auth = ":0", None

# 2. X11 connection to Xwayland
print("\n[2] Testing X11 connection to Xwayland...")
env = {**os.environ}
if display:
    env["DISPLAY"] = display
if auth:
    env["XAUTHORITY"] = auth

r = subprocess.run(["xdpyinfo"], env=env, capture_output=True, timeout=5)
results["x11_connection"] = r.returncode == 0
if results["x11_connection"]:
    lines = r.stdout.decode().splitlines()
    print(f" ✅ {lines[0] if lines else 'Connected'}")
else:
    print(f" ❌ {r.stderr.decode()[:80]}")

# 3. xdotool on Xwayland
print("\n[3] Testing xdotool on Xwayland...")
r = subprocess.run(
    ["xdotool", "getmouselocation"],
    env=env, capture_output=True, timeout=5
)
results["xdotool"] = r.returncode == 0
if results["xdotool"]:
    print(f" ✅ {r.stdout.decode().strip()[:40]}")
else:
    print(f" ❌ {r.stderr.decode()[:60]}")

# 4. x11vnc running
print("\n[4] Checking x11vnc...")
r = subprocess.run(["pgrep", "-f", "x11vnc"], capture_output=True)
results["x11vnc"] = r.returncode == 0
print(f" {'✅ running' if results['x11vnc'] else '❌ not running'}")
if not results["x11vnc"]:
    print(f" → bash start_xwayland_vnc.sh")

# 5. Port 5900
print("\n[5] Checking port 5900...")
try:
    s = socket.socket()
    s.settimeout(2)
    s.connect(("localhost", 5900))
    s.close()
    results["port_5900"] = True
    print(f" ✅ Port 5900 open")
except Exception as e:
    results["port_5900"] = False
    print(f" ❌ {e}")

# 6. VNC input test
if results.get("port_5900"):
    print("\n[6] Testing VNC input on Xwayland...")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from vnc_input import VNCInput
        
        # Get position before
        r = subprocess.run(
            ["xdotool", "getmouselocation"],
            env=env, capture_output=True
        )
        pos_before = r.stdout.decode().strip()

        # Move via VNC
        vnc = VNCInput()
        vnc.move(700, 500)
        time.sleep(0.5)
        vnc.close()

        # Get position after
        r = subprocess.run(
            ["xdotool", "getmouselocation"],
            env=env, capture_output=True
        )
        pos_after = r.stdout.decode().strip()

        moved = pos_before != pos_after
        results["vnc_input"] = moved
        print(f" Before: {pos_before}")
        print(f" After:  {pos_after}")
        print(f" {'✅ Mouse moved via VNC!' if moved else '❌ Mouse did not move'}")
    except Exception as e:
        results["vnc_input"] = False
        print(f" ❌ {e}")
else:
    results["vnc_input"] = False
    print(f"\n[6] VNC input : ⏭ skipped (port not open)")

# 7. Screenshot
print("\n[7] Desktop screenshot...")
try:
    r = subprocess.run(
        ["scrot", "-o", "/tmp/xwayland_verify.png"],
        env=env, capture_output=True, timeout=5
    )
    if r.returncode == 0:
        size = os.path.getsize("/tmp/xwayland_verify.png")
        results["screenshot"] = size > 200000
        print(f" {'✅' if results['screenshot'] else '⚠️'} {size:,} bytes")
    else:
        results["screenshot"] = False
        print(f" ❌ scrot failed")
except Exception as e:
    results["screenshot"] = False
    print(f" ❌ {e}")

# Summary
print(f"\n{'='*60}")
passed = sum(1 for v in results.values() if v is True)
total = len([v for v in results.values() if v is not None])
print(f"Results: {passed}/{total} checks passed")
for k, v in results.items():
    if v is None:
        print(f" ⏭ {k}")
    else:
        print(f" {'✅' if v else '❌'} {k}")

if results.get("vnc_input"):
    print(f"\n✅ SUCCESS!")
    print(f" VNC input reaches Xwayland")
    print(f" OpenClaw service can control desktop")
    print(f" Ready for V.1-V.5 tests")
elif results.get("x11_connection") and results.get("xdotool"):
    print(f"\n⚠️ Xwayland found but x11vnc not working properly")
    print(f" Run: bash start_xwayland_vnc.sh")
    print(f" Then: python3 verify_xwayland_vnc.py")
else:
    print(f"\n❌ Xwayland not found or not connecting")
print("="*60)
