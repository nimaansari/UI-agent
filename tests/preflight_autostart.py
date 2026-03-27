#!/usr/bin/env python3
# preflight_autostart.py — Pre-flight checks for autostart setup

import os, subprocess, shutil, time

print("=" * 55)
print("AUTOSTART PRE-FLIGHT CHECK")
print("=" * 55)

ok = True

# 1. Session type
session = os.environ.get("XDG_SESSION_TYPE", "unknown")
is_x11 = session == "x11"
print(f"\n[1] Session type : {session}")
print(f" {'✅ X11 — xdotool will work' if is_x11 else '❌ Not X11 — switch to GNOME on Xorg'}")
if not is_x11:
    ok = False

# 2. DISPLAY
display = os.environ.get("DISPLAY", "")
print(f"\n[2] DISPLAY : {display or 'not set'}")
print(f" {'✅' if display else '❌ not set'}")
if not display:
    ok = False

# 3. XAUTHORITY
xauth = os.environ.get("XAUTHORITY", "")
xauth_exists = os.path.exists(xauth) if xauth else False
print(f"\n[3] XAUTHORITY : {xauth or 'not set'}")
print(f" {'✅ exists' if xauth_exists else '❌ file not found'}")

# 4. Autostart file
autostart = os.path.expanduser("~/.config/autostart/openclaw-display.desktop")
print(f"\n[4] Autostart file : {'✅ exists' if os.path.exists(autostart) else '❌ not created'}")
if not os.path.exists(autostart):
    ok = False

# 5. Display helper script
helper = os.path.expanduser("~/.openclaw/start_display.sh")
print(f"\n[5] Display helper : {'✅ exists' if os.path.exists(helper) else '❌ not created'}")
if not os.path.exists(helper):
    ok = False

# 6. Display env file
env_file = os.path.expanduser("~/.openclaw/display_env.sh")
print(f"\n[6] Display env file : {'✅ exists' if os.path.exists(env_file) else '⚠️ not yet (created on first X11 login)'}")
if os.path.exists(env_file):
    with open(env_file) as f:
        content = f.read().strip()
        print(f" Contents: {content}")

# 7. xdotool installed
xdotool_ok = bool(shutil.which("xdotool"))
print(f"\n[7] xdotool : {'✅' if xdotool_ok else '❌ sudo apt-get install xdotool'}")
if not xdotool_ok:
    ok = False

# 8. scrot installed
scrot_ok = bool(shutil.which("scrot"))
print(f"\n[8] scrot : {'✅' if scrot_ok else '❌ sudo apt-get install scrot'}")

# 9. x11vnc installed
x11vnc_ok = bool(shutil.which("x11vnc"))
print(f"\n[9] x11vnc : {'✅' if x11vnc_ok else '❌ sudo apt-get install x11vnc'}")

print(f"\n{'='*55}")
if ok:
    print("✅ Pre-flight passed — ready to run tests")
else:
    print("❌ Fix issues above first")
    if not is_x11:
        print("\nCritical: Log out → gear icon → GNOME on Xorg → log in")
print("="*55)

if not ok:
    exit(1)
