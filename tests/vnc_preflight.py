#!/usr/bin/env python3
# vnc_preflight.py
# Pre-flight checks for VNC setup

import subprocess, socket, os, time

print("=" * 55)
print("VNC PRE-FLIGHT CHECK")
print("=" * 55)

ok = True

# 1. x11vnc
r = subprocess.run(["pgrep", "-f", "x11vnc"], capture_output=True)
vnc_ok = r.returncode == 0
print(f" x11vnc running : {'✅' if vnc_ok else '❌ run: bash start_vnc.sh'}")
if not vnc_ok: ok = False

# 2. Port 5900
try:
 s = socket.socket(); s.settimeout(1)
 s.connect(("localhost", 5900)); s.close()
 print(f" Port 5900 : ✅")
except:
 print(f" Port 5900 : ❌ VNC not listening")
 ok = False

# 3. DISPLAY :0
display = os.environ.get("DISPLAY", "")
print(f" DISPLAY : {display}")

# 4. XAUTHORITY
uid = os.getuid()
xauth = None
try:
 for f in os.listdir(f"/run/user/{uid}"):
 if "Xwaylandauth" in f:
 xauth = f"/run/user/{uid}/{f}"
 break
except:
 pass
print(f" XAUTHORITY : {'✅ ' + str(xauth) if xauth else '❌ not found'}")
if not xauth: ok = False

# 5. scrot
import shutil
scrot_ok = bool(shutil.which("scrot"))
print(f" scrot : {'✅' if scrot_ok else '❌ sudo apt-get install scrot'}")

print(f"\n{'✅ Ready' if ok else '❌ Fix issues above first'}")
if not ok: exit(1)
