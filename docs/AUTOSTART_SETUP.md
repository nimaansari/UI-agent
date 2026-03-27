# OpenClaw Autostart with Display Access on X11 Login

## What This Does

When you log into GNOME on Xorg (after switching from Wayland):
1. OpenClaw starts automatically (as it does now)
2. A display helper also starts automatically
3. The helper sets DISPLAY=:0 and starts x11vnc
4. OpenClaw now has full desktop access
5. User sees Chrome live on their desktop

No manual steps after switching to X11 session.

---

## Step 1 — Create the Display Helper Script

This script runs at login, sets up display access, and starts x11vnc.

Save as `~/.openclaw/start_display.sh`:

```bash
#!/bin/bash
# ~/.openclaw/start_display.sh
# Runs at X11 login to give OpenClaw desktop access
# Place in GNOME autostart so it fires after login

LOG="/tmp/openclaw_display.log"
exec > "$LOG" 2>&1

echo "[$(date)] OpenClaw display helper starting..."

# Wait for desktop to fully load
sleep 3

# Verify we're on X11
SESSION=$(echo $XDG_SESSION_TYPE)
echo "Session type: $SESSION"

if [ "$SESSION" != "x11" ]; then
 echo "❌ Not on X11 session — display helper only works on GNOME on Xorg"
 exit 1
fi

# Export display variables for OpenClaw
export DISPLAY=:0
export XAUTHORITY=$XAUTHORITY

echo "DISPLAY : $DISPLAY"
echo "XAUTHORITY : $XAUTHORITY"

# Test X11 connection
xdpyinfo -display :0 > /dev/null 2>&1
if [ $? -ne 0 ]; then
 echo "❌ Cannot connect to X11 display :0"
 exit 1
fi
echo "✅ X11 connection verified"

# Write display vars to a file OpenClaw can read
mkdir -p ~/.openclaw
cat > ~/.openclaw/display_env.sh << EOF
export DISPLAY=:0
export XAUTHORITY=$XAUTHORITY
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
EOF
echo "✅ Display env written to ~/.openclaw/display_env.sh"

# Start x11vnc for live visibility
pkill -f x11vnc 2>/dev/null
sleep 1

x11vnc \
 -display :0 \
 -auth "$XAUTHORITY" \
 -forever \
 -nopw \
 -bg \
 -rfbport 5900 \
 -xkb \
 -noxdamage \
 -quiet

sleep 2

if pgrep -f x11vnc > /dev/null; then
 echo "✅ x11vnc started on port 5900"
else
 echo "⚠️ x11vnc failed — display still works, just no VNC view"
fi

# Signal OpenClaw that display is ready
touch ~/.openclaw/display_ready

echo "[$(date)] Display helper complete ✅"
```

```bash
chmod +x ~/.openclaw/start_display.sh
```

---

## Step 2 — Add to GNOME Autostart

GNOME autostart entries live in `~/.config/autostart/`.
Any `.desktop` file there runs automatically at login.

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/openclaw-display.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=OpenClaw Display Helper
Comment=Gives OpenClaw access to the desktop display
Exec=/bin/bash /home/nimapro1381/.openclaw/start_display.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=3
EOF
```

Verify it was created:
```bash
cat ~/.config/autostart/openclaw-display.desktop
```

---

## Step 3 — Update OpenClaw to Read Display Env

Create `openclaw_display_init.py` in your OpenClaw directory:

```python
#!/usr/bin/env python3
# openclaw_display_init.py
# Add this to OpenClaw's startup sequence

import os
import time
import subprocess

def init_display(timeout=30):
    """
    Wait for display helper to run and read display variables.
    Call this at OpenClaw startup before any automation.
    """
    display_env = os.path.expanduser("~/.openclaw/display_env.sh")
    display_ready = os.path.expanduser("~/.openclaw/display_ready")

    print("[display] Waiting for display access...")

    # Wait for display helper to signal ready
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(display_ready):
            break
        time.sleep(1)

    if not os.path.exists(display_ready):
        print("[display] ⚠️ Display helper did not run — using fallback")
        _fallback_display()
        return

    # Read display variables from file
    if os.path.exists(display_env):
        with open(display_env) as f:
            for line in f:
                line = line.strip()
                if line.startswith("export "):
                    line = line[7:]
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key] = val
                    print(f"[display] {key}={val}")

    display = os.environ.get("DISPLAY", "")
    if display:
        print(f"[display] ✅ Display access ready: {display}")
    else:
        print("[display] ⚠️ No DISPLAY set after reading env")
        _fallback_display()


def _fallback_display():
    """Fallback: try to detect display without the helper."""
    # Try :0
    os.environ["DISPLAY"] = ":0"
    os.environ["GDK_BACKEND"] = "x11"
    print(f"[display] Fallback: DISPLAY=:0")


if __name__ == "__main__":
    init_display()
    print(f"\nFinal environment:")
    print(f" DISPLAY = {os.environ.get('DISPLAY', 'not set')}")
    print(f" XAUTHORITY = {os.environ.get('XAUTHORITY', 'not set')}")
```

Update `chrome_session.py` to call this at startup:

```python
# At the top of get_ctrl() function:

def get_ctrl():
    global _proc, _ctrl

    # Initialize display on first call
    if "DISPLAY" not in os.environ or not os.environ["DISPLAY"]:
        try:
            from openclaw_display_init import init_display
            init_display()
        except:
            pass

    # ... rest of get_ctrl() unchanged
```

---

## Step 4 — Verify Autostart Works

Create `verify_autostart.py`:

```python
#!/usr/bin/env python3
# verify_autostart.py

import os, time, subprocess, sys

print("=" * 55)
print("Autostart Verification")
print("=" * 55)

# 1. Display env file created
display_env = os.path.expanduser("~/.openclaw/display_env.sh")
exists = os.path.exists(display_env)
print(f"\n[1] Display env file : {'✅' if exists else '❌'}")
if exists:
    with open(display_env) as f:
        lines = f.read().strip().split('\n')
        for line in lines[:3]:
            print(f" {line}")

# 2. Display ready signal
ready = os.path.exists(os.path.expanduser("~/.openclaw/display_ready"))
print(f"\n[2] Display ready signal : {'✅' if ready else '❌'}")

# 3. Initialize display
try:
    sys.path.insert(0, '.')
    from openclaw_display_init import init_display
    init_display(timeout=5)
except:
    pass

display = os.environ.get("DISPLAY", "")
xauth = os.environ.get("XAUTHORITY", "")
print(f"\n[3] DISPLAY : {'✅ ' + display if display else '❌'}")
print(f"[4] XAUTHORITY : {'✅' if xauth else '❌'}")

# 5. xdotool works
r = subprocess.run(
    ["xdotool", "getmouselocation"],
    env={**os.environ},
    capture_output=True
)
xdotool_works = r.returncode == 0
print(f"\n[5] xdotool : {'✅' if xdotool_works else '❌'}")

# 6. x11vnc running
r = subprocess.run(["pgrep", "-f", "x11vnc"], capture_output=True)
vnc_running = r.returncode == 0
print(f"\n[6] x11vnc : {'✅' if vnc_running else '⚠️'}")

print(f"\n{'='*55}")
if xdotool_works and display:
    print("✅ Autostart configured correctly")
    print(" Desktop access ready")
else:
    print("⚠️ Check /tmp/openclaw_display.log")
print("="*55)
```

---

## Complete Setup (One Time)

```bash
# 1. Create display helper script
mkdir -p ~/.openclaw
cat > ~/.openclaw/start_display.sh << 'SCRIPT'
# (paste script from Step 1 above)
SCRIPT
chmod +x ~/.openclaw/start_display.sh

# 2. Create autostart desktop file
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/openclaw-display.desktop << 'DESKTOP'
# (paste desktop file from Step 2 above)
DESKTOP

# 3. Create display init module
cat > openclaw_display_init.py << 'PYTHON'
# (paste python code from Step 3 above)
PYTHON

# 4. Update chrome_session.py
# Add init_display() call to get_ctrl() (see Step 3)

# 5. Switch to X11 session (one time!)
# Log out → GNOME login screen gear icon → "GNOME on Xorg" → log in

# 6. Log back in to X11, verify:
python3 verify_autostart.py
```

---

## What Happens After Setup

```
You log in to GNOME on Xorg
    ↓
GNOME autostart runs openclaw-display.sh
    ↓
Sets DISPLAY=:0, starts x11vnc, creates display_ready
    ↓
OpenClaw starts (as normal)
    ↓
chrome_session.py calls init_display()
    ↓
Reads ~/.openclaw/display_env.sh
    ↓
Chrome launches on real X11 desktop (visible!)
xdotool works (no VirtualBox blocking)
x11vnc gives live view on port 5900
```

---

## If Something Goes Wrong

```bash
# Check the startup log
cat /tmp/openclaw_display.log

# Manually test display
DISPLAY=:0 xdotool getmouselocation

# Manually start x11vnc
DISPLAY=:0 XAUTHORITY=$XAUTHORITY x11vnc -forever -nopw &
```

---

## Summary

**One-time steps:**
1. Copy autostart script to ~/.openclaw/
2. Create autostart desktop entry
3. Switch to X11 session (2 min)
4. Everything runs automatically after that

**After that:** 
- Log in to X11 → OpenClaw has desktop access automatically
- Chrome visible on desktop
- xdotool works
- x11vnc runs (if needed for remote viewing)
