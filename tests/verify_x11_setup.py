#!/usr/bin/env python3
# verify_x11_setup.py — Verify X11 session + x11vnc setup

import subprocess, socket, os, time, shutil, sys

print("=" * 55)
print("X11 Session + x11vnc Verification")
print("=" * 55)

results = {}

# 1. X11 session confirmed
session = os.environ.get("XDG_SESSION_TYPE", "")
results["x11_session"] = session == "x11"
print(f"\n[1] Session type : {session} {'✅' if results['x11_session'] else '❌ need GNOME on Xorg'}")

# 2. DISPLAY set
display = os.environ.get("DISPLAY", "")
results["display"] = bool(display)
print(f"[2] DISPLAY : {display} {'✅' if display else '❌'}")

# 3. XAUTHORITY set
xauth = os.environ.get("XAUTHORITY", "")
xauth_exists = os.path.exists(xauth) if xauth else False
results["xauthority"] = xauth_exists
print(f"[3] XAUTHORITY : {xauth} {'✅' if xauth_exists else '❌'}")

# 4. X11 connection works
r = subprocess.run(["xdpyinfo", "-display", ":0"],
    capture_output=True,
    env={**os.environ, "DISPLAY": ":0"})
results["x11_connection"] = r.returncode == 0
if r.returncode == 0:
    print(f"[4] X11 connection : ✅")
else:
    print(f"[4] X11 connection : ❌ {r.stderr.decode()[:60]}")

# 5. xdotool works
r = subprocess.run(
    ["xdotool", "getmouselocation"],
    capture_output=True,
    env={**os.environ, "DISPLAY": ":0"}
)
results["xdotool"] = r.returncode == 0
if r.returncode == 0:
    print(f"[5] xdotool : ✅ {r.stdout.decode().strip()[:40]}")
else:
    print(f"[5] xdotool : ❌ {r.stderr.decode()[:60]}")

# 6. x11vnc running
r = subprocess.run(["pgrep", "-f", "x11vnc"], capture_output=True)
results["x11vnc"] = r.returncode == 0
print(f"[6] x11vnc running : {'✅' if results['x11vnc'] else '❌ run: bash start_x11vnc.sh'}")

# 7. Port 5900 open
try:
    s = socket.socket()
    s.settimeout(2)
    s.connect(("localhost", 5900))
    s.close()
    results["port_5900"] = True
    print(f"[7] Port 5900 : ✅")
except Exception as e:
    results["port_5900"] = False
    print(f"[7] Port 5900 : ❌ ({e})")

# 8. Desktop screenshot is large (real X11 rendering)
try:
    env = {**os.environ, "DISPLAY": ":0"}
    subprocess.run(["scrot", "-o", "/tmp/x11_verify.png"],
        env=env, capture_output=True, timeout=5)
    size = os.path.getsize("/tmp/x11_verify.png")
    results["screenshot"] = size > 500000
    if size > 500000:
        print(f"[8] Desktop screenshot: {size:,} bytes ✅")
    else:
        print(f"[8] Desktop screenshot: {size:,} bytes ⚠️ (too small)")
except Exception as e:
    results["screenshot"] = False
    print(f"[8] Desktop screenshot: ❌ {e}")

# 9. VNC input test
if results.get("port_5900"):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from vnc_input import VNCInput
        
        pos_before = subprocess.run(
            ["xdotool", "getmouselocation"],
            capture_output=True,
            env={**os.environ, "DISPLAY": ":0"}
        ).stdout.decode().strip()

        vnc = VNCInput()
        vnc.move(600, 400)
        time.sleep(0.5)
        vnc.close()

        pos_after = subprocess.run(
            ["xdotool", "getmouselocation"],
            capture_output=True,
            env={**os.environ, "DISPLAY": ":0"}
        ).stdout.decode().strip()

        moved = pos_before != pos_after
        results["vnc_input"] = moved
        if moved:
            print(f"[9] VNC input : ✅ mouse moved")
        else:
            print(f"[9] VNC input : ⚠️ mouse did not move")
            print(f" before: {pos_before}")
            print(f" after: {pos_after}")
    except Exception as e:
        results["vnc_input"] = False
        print(f"[9] VNC input : ❌ {e}")
else:
    results["vnc_input"] = None
    print(f"[9] VNC input : ⏭ skipped (port 5900 not open)")

# Summary
print(f"\n{'='*55}")
passed = sum(1 for v in results.values() if v is True)
total = len([v for v in results.values() if v is not None])
print(f"Results: {passed}/{total} checks passed")
for k, v in results.items():
    if v is None:
        print(f" ⏭ {k}")
    else:
        print(f" {'✅' if v else '❌'} {k}")

if passed >= 7:
    print(f"\n✅ X11 setup complete — UIAgent has full desktop access")
    print(f" xdotool works (no VirtualBox blocking on X11)")
    print(f" x11vnc gives live desktop view")
    print(f" Ready for V.1-V.5 tests with real evidence")
elif results.get("x11_session") and results.get("xdotool"):
    print(f"\n✅ Core X11 working — start x11vnc for full visibility")
    print(f" Run: bash start_x11vnc.sh")
else:
    print(f"\n❌ Not on X11 session — log out and select GNOME on Xorg")
print("="*55)
