#!/usr/bin/env python3
# verify_wayvnc.py — Verify wayvnc setup for Wayland desktop

import subprocess, socket, os, time, sys, shutil

print("=" * 55)
print("wayvnc Verification")
print("=" * 55)

results = {}

# 1. wayvnc installed
installed = bool(shutil.which("wayvnc"))
results["wayvnc_installed"] = installed
print(f"\n[1] wayvnc installed : {'✅' if installed else '❌ sudo apt-get install wayvnc'}")

# 2. wayvnc running
r = subprocess.run(["pgrep", "-f", "wayvnc"], capture_output=True)
running = r.returncode == 0
results["wayvnc_running"] = running
print(f"[2] wayvnc running : {'✅' if running else '❌ run: bash start_wayvnc.sh'}")

# 3. Port 5900 open
try:
    s = socket.socket()
    s.settimeout(2)
    s.connect(("localhost", 5900))
    s.close()
    results["port_5900"] = True
    print(f"[3] Port 5900 open : ✅")
except Exception as e:
    results["port_5900"] = False
    print(f"[3] Port 5900 open : ❌ ({e})")

# 4. Wayland session
wayland = os.environ.get("WAYLAND_DISPLAY", "")
results["wayland_session"] = bool(wayland)
print(f"[4] WAYLAND_DISPLAY : {'✅ ' + wayland if wayland else '❌ not set'}")

# 5. VNC input test
if results.get("port_5900"):
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from vnc_input import VNCInput
        vnc = VNCInput()
        vnc.move(960, 540)
        time.sleep(0.3)
        vnc.move(100, 100)
        results["vnc_input"] = True
        print(f"[5] VNC input : ✅ mouse moved")
        print(f" → Mouse cursor should have moved on your desktop")
        vnc.close()
    except Exception as e:
        results["vnc_input"] = False
        print(f"[5] VNC input : ❌ {e}")
else:
    results["vnc_input"] = False
    print(f"[5] VNC input : ⏭ skipped (port 5900 not open)")

# 6. Screenshot desktop
try:
    env = {**os.environ}
    r = subprocess.run(
        ["scrot", "-o", "/tmp/wayvnc_verify.png"],
        env=env, capture_output=True, timeout=5
    )
    if r.returncode == 0:
        size = os.path.getsize("/tmp/wayvnc_verify.png")
        results["screenshot"] = size > 200000
        status = "✅" if results["screenshot"] else "⚠️"
        print(f"[6] Desktop screenshot : {status} {size:,} bytes")
        if size < 200000:
            print(f" → Screenshot small — may be rendering offscreen")
    else:
        results["screenshot"] = False
        print(f"[6] Desktop screenshot : ❌ scrot failed")
except Exception as e:
    results["screenshot"] = False
    print(f"[6] Desktop screenshot : ❌ {e}")

# 7. Chrome on Wayland desktop
print(f"\n[7] Testing Chrome on Wayland desktop...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from chrome_session_display0 import get_ctrl, reset
    ctrl = get_ctrl()
    reset("https://example.com", wait=3)
    time.sleep(2)
    title = ctrl.js("document.title") or ""
    url = ctrl.js("window.location.href") or ""
    results["chrome"] = bool(title)
    print(f" {'✅' if title else '❌'} Chrome title: '{title}'")
    print(f" URL: {url}")
    if title:
        print(f" → Chrome window should be visible on your Wayland desktop")
except Exception as e:
    results["chrome"] = False
    print(f" ❌ Chrome failed: {e}")

# Summary
print(f"\n{'='*55}")
passed = sum(1 for v in results.values() if v)
print(f"Results: {passed}/{len(results)} checks passed")
for k, v in results.items():
    print(f" {'✅' if v else '❌'} {k}")

if passed >= 5:
    print(f"\n✅ wayvnc working — UIAgent has Wayland desktop access")
elif results.get("port_5900") and results.get("vnc_input"):
    print(f"\n✅ Core VNC working — Chrome visibility may need adjustment")
else:
    print(f"\n⚠️ Fix failing checks — see notes above")
print("="*55)
