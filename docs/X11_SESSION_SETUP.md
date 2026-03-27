# Switch to X11 Session + x11vnc Setup

## Why This Works

VirtualBox blocks Wayland protocols (screencopy, virtual pointer).
X11 session uses Xorg instead of Mutter/Wayland.
Xorg works fine inside VirtualBox.
x11vnc connects to Xorg directly — no compositor protocols needed.

---

## Step 1 — Switch to X11 Session

**Do this on the physical machine (not via SSH):**

1. Click your username at the top right of the login screen
2. Click the **gear icon** at the bottom right
3. Select **"GNOME on Xorg"**
4. Enter your password and log in

Or from terminal:
```bash
# Log out current session
gnome-session-quit --logout --no-prompt

# At login screen: gear icon → GNOME on Xorg → login
```

**Verify you're on X11 after logging in:**
```bash
echo $XDG_SESSION_TYPE
# Must show: x11
# If it shows: wayland — you're still on Wayland, repeat step 1
```

---

## Step 2 — Verify X11 Environment

```bash
# All of these must return values
echo "Session type : $XDG_SESSION_TYPE" # must be: x11
echo "Display : $DISPLAY" # must be: :0
echo "Xauthority : $XAUTHORITY" # must be a file path

# Test X11 connection
xdpyinfo -display :0 | head -5
# Must show display info, not an error
```

---

## Step 3 — Start x11vnc

```bash
# Find XAUTHORITY (X11 session uses a different path than Wayland)
echo $XAUTHORITY

# Start x11vnc
x11vnc \
 -display :0 \
 -auth $XAUTHORITY \
 -forever \
 -nopw \
 -bg \
 -rfbport 5900 \
 -xkb \
 -quiet

# Verify port is open
sleep 2
ss -tlnp | grep 5900
```

Save as `start_x11vnc.sh`:

```bash
#!/bin/bash
# start_x11vnc.sh — for X11 (Xorg) sessions only

# Verify we're on X11
SESSION=$(echo $XDG_SESSION_TYPE)
if [ "$SESSION" != "x11" ]; then
 echo "❌ Not on X11 session (detected: $SESSION)"
 echo " Log out and select 'GNOME on Xorg' at login screen"
 exit 1
fi

echo "Session type : $SESSION ✅"
echo "Display : $DISPLAY"
echo "XAUTHORITY : $XAUTHORITY"

# Kill existing x11vnc
pkill -f x11vnc 2>/dev/null
sleep 1

# Start x11vnc
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

sleep 1.5

if pgrep -f x11vnc > /dev/null; then
 echo "✅ x11vnc started on port 5900"
 echo " Connect: xtightvncviewer localhost:5900"
else
 echo "❌ x11vnc failed"
 echo " Try: x11vnc -display :0 -auth $XAUTHORITY -forever -nopw"
fi
```

```bash
chmod +x start_x11vnc.sh
bash start_x11vnc.sh
```

---

## Step 4 — Connect VNC Viewer

```bash
xtightvncviewer localhost:5900 &
```

You should see your full desktop inside a VNC window.
This confirms x11vnc is working.

---

## Step 5 — Verify xdotool Works on X11

On X11, xdotool is no longer blocked by VirtualBox.
Test it:

```bash
# Move mouse to center of screen
xdotool mousemove 960 540
# Mouse should visibly move

# Click
xdotool click 1
# Should register a click

# Type
xdotool type "hello from xdotool"
# Should type into focused window
```

If these work, xdotool is fully functional on X11.
No VNC input bypass needed — xdotool works directly.

---

## Step 6 — Verify X11 + x11vnc Setup

Create and run verification script:

```bash
python3 tests/verify_x11_setup.py
```

This checks:
- ✅ X11 session active
- ✅ DISPLAY and XAUTHORITY set
- ✅ X11 connection works
- ✅ xdotool functional
- ✅ x11vnc running
- ✅ Port 5900 open
- ✅ Desktop screenshot > 500KB (real rendering)
- ✅ VNC input moves mouse

---

## Step 7 — Run UIAgent Tests

Once X11 is verified, run the full V.1-V.5 test suite:

```bash
python3 tests/test_vnc_v1_chrome_visible.py
python3 tests/test_vnc_v2_click.py
python3 tests/test_vnc_v3_click_chrome.py
python3 tests/test_vnc_v4_desktop_app.py
python3 tests/test_vnc_v5_full_workflow.py
```

Each test will show raw BEFORE/AFTER measured values:
```
BEFORE URL    : https://example.com
AFTER URL     : https://different.com
BEFORE hash   : a3f8c2d1...
AFTER hash    : 7b9e4f2a... (different)
Screenshot    : 1,245,892 bytes (real X11 desktop)
✅ TEST PASSED
```

---

## What Changes on X11 vs Wayland

| Feature | Wayland (current) | X11 (after switch) |
|---------|-------------------|-------------------|
| xdotool clicks | ❌ blocked by VB | ✅ works directly |
| x11vnc | ❌ fails | ✅ works |
| wayvnc | ❌ VB blocks screencopy | not needed |
| Desktop screenshots | Small/blank | Large (1-3MB) |
| Live desktop view | Not possible | Via x11vnc ✅ |
| CDP browser clicks | ✅ always works | ✅ always works |
| UIAgent overall | Browser only | Browser + Desktop |

---

## Complete Setup Order

```bash
# On the physical machine:
# 1. Log out
# 2. At login screen: gear icon → "GNOME on Xorg" → log in

# Then in terminal:
# 3. Verify X11
echo $XDG_SESSION_TYPE  # must show: x11

# 4. Test xdotool works
xdotool mousemove 960 540

# 5. Start x11vnc
bash start_x11vnc.sh

# 6. View desktop (optional, confirms VNC works)
xtightvncviewer localhost:5900 &

# 7. Verify full setup
python3 tests/verify_x11_setup.py

# 8. Run UIAgent tests
python3 tests/test_vnc_v1_chrome_visible.py
python3 tests/test_vnc_v3_click_chrome.py
# ... etc
```

---

## Important Notes

- **X11 session switch requires logout/login** — can't do via SSH
- **x11vnc must run in X11 session** — won't work in Wayland session
- **Desktop screenshots will be > 500KB** — sign of real X11 rendering
- **xdotool works without VNC** — VirtualBox doesn't block X11 input
- **VNC is optional** — xdotool alone gives full desktop control
- **V.1-V.5 tests will show real evidence** — hashes, URLs, file content

---

## Troubleshooting

### "Not on X11 session"
- Log out completely
- At GNOME login screen, click the ⚙️ gear icon
- Select "GNOME on Xorg" from the dropdown
- Log in with your password

### "x11vnc failed: XAUTHORITY not found"
```bash
# Check XAUTHORITY
echo $XAUTHORITY
# Should show a file path like: /home/user/.Xauthority

# If empty, set it manually
export XAUTHORITY=$HOME/.Xauthority
bash start_x11vnc.sh
```

### "xdotool: error: Unable to connect to X server"
```bash
# Check DISPLAY
echo $DISPLAY
# Must be: :0

# Set if empty
export DISPLAY=:0
xdotool mousemove 960 540
```

### Port 5900 already in use
```bash
# Kill existing x11vnc
pkill -f x11vnc
sleep 2

# Or use different port
x11vnc -display :0 -auth $XAUTHORITY -forever -nopw -rfbport 5901
```

---

## After Switching to X11

UIAgent gains:
- ✅ xdotool input injection (not blocked)
- ✅ x11vnc VNC server
- ✅ Real-time desktop visibility
- ✅ Full V.1-V.5 test suite with real evidence
- ✅ Desktop app automation (xterm, gedit, nautilus)

No code changes needed — all infrastructure is compatible.
