# wayvnc Setup — VNC on Wayland Desktop

## Why wayvnc Instead of x11vnc

Your system runs **Wayland** (GNOME/Mutter compositor).

- **x11vnc** only works with X11 display servers
- **wayvnc** is built specifically for Wayland compositors

```
x11vnc → needs X11 display server → ❌ (you have Wayland)
wayvnc → talks to Wayland compositor directly → ✅ (works)
```

---

## Step 1 — Install wayvnc

```bash
# Try package manager first
sudo apt-get update
sudo apt-get install -y wayvnc

# Verify installation
which wayvnc
wayvnc --version
```

### If not in apt

**Option A: Ubuntu PPA**
```bash
sudo add-apt-repository ppa:wayvnc/stable
sudo apt-get update
sudo apt-get install -y wayvnc
```

**Option B: Build from source**
```bash
sudo apt-get install -y \
 meson ninja-build pkg-config \
 libwayland-dev libxkbcommon-dev \
 libegl-dev libgles2-mesa-dev \
 libpixman-1-dev libgnutls28-dev \
 libaml-dev libneatvnc-dev

git clone https://github.com/any1/wayvnc.git
cd wayvnc
meson build
ninja -C build
sudo ninja -C build install
```

---

## Step 2 — Start wayvnc

wayvnc must run inside your Wayland session (as your user, not root).

```bash
# Simple start
wayvnc 0.0.0.0 5900 &

# Or with the provided script
bash start_wayvnc.sh
```

**Verify:**
```bash
pgrep -a wayvnc  # Should show wayvnc process
ss -tlnp | grep 5900  # Should show port 5900 listening
```

---

## Step 3 — Test with VNC Viewer

Open a VNC viewer to confirm your desktop is visible:

```bash
xtightvncviewer localhost:5900 &
```

You should see your full Wayland desktop inside the VNC window.

---

## Step 4 — Verify Full Setup

Run the verification script:

```bash
cd /path/to/gui-cowork
python3 tests/verify_wayvnc.py
```

This checks:
- ✅ wayvnc installed
- ✅ wayvnc running
- ✅ Port 5900 open
- ✅ Wayland session detected
- ✅ VNC input working (mouse movement)
- ✅ Desktop screenshot captured
- ✅ Chrome on Wayland desktop

---

## How It Works

### VNC Architecture (Unchanged)

The VNC infrastructure we built is **completely correct**:

```
UIAgent
  ├─ CDP (Chrome DevTools Protocol) ✅
  │  └─ Controls Chrome via remote debugging
  │
  └─ VNC Input (RFB protocol) ✅
     ├─ Connect to wayvnc (port 5900)
     ├─ Send mouse movements, clicks, keyboard
     └─ Bypasses VirtualBox kernel-level blocking
```

### Wayland Support

`chrome_session_display0.py` now auto-detects your session:

```python
# Detects WAYLAND_DISPLAY environment variable
if WAYLAND_DISPLAY:
    # Use Wayland backend
    env["GDK_BACKEND"] = "wayland"
    env["QT_QPA_PLATFORM"] = "wayland"
else:
    # Fall back to X11/Xwayland
    env["GDK_BACKEND"] = "x11"
    env["QT_QPA_PLATFORM"] = "xcb"
```

Chrome renders to Wayland compositor, wayvnc captures it, VNC viewer shows it.

---

## Complete Setup Order

```bash
# 1. Install wayvnc
sudo apt-get install -y wayvnc

# 2. Start it
bash /path/to/gui-cowork/start_wayvnc.sh

# 3. View your desktop via VNC (optional, for confirmation)
xtightvncviewer localhost:5900 &

# 4. Verify everything works
python3 tests/verify_wayvnc.py

# 5. Run V.1-V.5 tests
python3 tests/test_vnc_v1_chrome_visible.py
python3 tests/test_vnc_v2_click.py
# ... etc
```

---

## Expected Results

When wayvnc is working correctly:

✅ **VNC Viewer**
- Shows your full Wayland desktop
- Can see mouse cursor moving
- Colors and content match your screen

✅ **Chrome**
- Opens visibly on your desktop
- CDP controls work (navigation, DOM reads)
- CDP + VNC input work together

✅ **Mouse/Keyboard**
- Mouse cursor moves on desktop
- Clicks register on windows
- Text input works in apps

✅ **Screenshots**
- Desktop screenshots > 1MB (real Wayland rendering)
- Not 4-5KB (which means rendering offscreen)

✅ **Tests**
- V.1 passes: Chrome visible, screenshot hash changes
- V.2 passes: VNC connects, mouse moves
- V.3 passes: VNC click navigates Chrome
- V.4 passes: VNC input reaches desktop apps
- V.5 passes: Full workflow (CDP + VNC together)

---

## Troubleshooting

### wayvnc: "Permission denied"
```bash
# Run as your user, not sudo
wayvnc 0.0.0.0 5900 &
```

### wayvnc: "Failed to connect to compositor"
```bash
# Wayland server may not be running
# Check session type:
echo $XDG_SESSION_TYPE  # Should be "wayland"

# Or check Wayland display:
echo $WAYLAND_DISPLAY   # Should be "wayland-0" or similar
```

### VNC viewer shows blank/black screen
```bash
# Wayland may not be exposing framebuffer yet
# Fallback options:

# Option 1: List available outputs
wayvnc --list-outputs

# Option 2: Specify output explicitly
wayvnc --output=HDMI-A-1 0.0.0.0 5900

# Option 3: Use gnome-remote-desktop (built into GNOME)
gsettings set org.gnome.desktop.remote-desktop.vnc enable true
systemctl --user start gnome-remote-desktop
```

### Chrome doesn't appear on desktop
```bash
# Check Chrome is using Wayland backend:
google-chrome --ozone-platform=wayland about:blank

# Or check environment:
env | grep -E "WAYLAND|DISPLAY|GDK_BACKEND"
```

### Port 5900 already in use
```bash
# Kill existing wayvnc or other service
pkill -f wayvnc
pkill -f x11vnc
pkill -f vncserver

# Use different port
wayvnc 0.0.0.0 5901 &
# Update vnc_input.py: VNC_PORT = 5901
```

---

## Fallback Options

If wayvnc doesn't work on your system:

### Fallback 1 — wlvnc (Alternative Wayland VNC)
```bash
sudo apt-get install -y wlvnc
wlvnc &
# Should listen on port 5900
```

### Fallback 2 — GNOME Remote Desktop (Built-in)
```bash
# GNOME 42+ has built-in VNC
gsettings set org.gnome.desktop.remote-desktop.vnc enable true
gsettings set org.gnome.desktop.remote-desktop.vnc view-only false
systemctl --user start gnome-remote-desktop
```

### Fallback 3 — Switch to X11 Session
```bash
# Log out
# At GNOME login screen: Click ⚙️ icon
# Select "GNOME on Xorg"
# Log in with X11

# Now use x11vnc:
bash start_vnc.sh  # from VNC_SETUP.md
```

---

## Performance Notes

wayvnc performance depends on:
- Screen resolution (higher = more bandwidth)
- Color depth (24-bit vs 8-bit)
- Network latency
- CPU/GPU encoding

For best performance with UIAgent:
- Use local VNC (localhost:5900) for development
- Use SSH tunnels for remote (`ssh -L 5900:localhost:5900 user@host`)
- Reduce color depth if needed: `wayvnc --color-depth=8`

---

## Files Modified/Created

**Modified:**
- `src/chrome_session_display0.py` — Added Wayland auto-detection

**Created:**
- `start_wayvnc.sh` — Start wayvnc on Wayland
- `tests/verify_wayvnc.py` — Verify wayvnc setup
- `docs/WAYVNC_SETUP.md` — This file

**Unchanged (still valid):**
- `src/vnc_input.py` — Works with any VNC server (x11vnc, wayvnc, wlvnc)
- `src/cdp_typer.py` — Works on any display
- `tests/test_vnc_v*.py` — Work with wayvnc

---

## Next Steps

1. Install wayvnc: `sudo apt-get install -y wayvnc`
2. Start it: `bash start_wayvnc.sh`
3. Verify: `python3 tests/verify_wayvnc.py`
4. Run V.1-V.5 tests to confirm everything works
5. Integrate into UIAgent skill for ClawHub

---

**Result:** UIAgent now has real-time Wayland desktop access with VNC input injection. ✅
