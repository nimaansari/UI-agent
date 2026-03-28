# UIAgent v1.0

Universal UI automation framework for browser and desktop automation.

## Features

- 🌐 **Browser Automation** — Chrome DevTools Protocol (CDP)
  - Navigate websites, fill forms, execute JavaScript
  - Screenshot capture, DOM manipulation
  - Works on any site, any browser

- 🖥️ **Desktop Automation** — Real desktop control
  - Screenshots of real desktop (565KB+ images)
  - Keyboard input via ydotool
  - Mouse clicks via pyatspi
  - Launch desktop applications
  - Works on Wayland + VirtualBox

- 🚀 **Headless Support** — Works from service context
  - No display required
  - OpenClaw compatible
  - Production-grade

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/nimaansari/UI-agent.git
cd UI-agent

# One-time setup
bash INSTALL_YDOTOOL.sh

# Install Python dependencies
pip install requests websocket-client pillow
```

### Browser Automation

```python
from src.chrome_session_display0 import get_ctrl, reset

# Launch Chrome
ctrl = get_ctrl()

# Navigate
reset("https://google.com")

# Fill form
ctrl.js('document.querySelector("input").value = "search term"')
ctrl.key("Return")

# Read DOM
title = ctrl.js("document.title")
```

### Desktop Automation

```python
from src.desktop_controller import DesktopController

ctrl = DesktopController()

# Screenshot
screenshot = ctrl.screenshot("/tmp/desktop.png")

# Type text
ctrl.type_text("hello world")

# Keyboard
ctrl.key("ctrl+s")
ctrl.key("Return")

# Mouse
ctrl.click(960, 540)
ctrl.double_click(500, 300)

# Open app
proc = ctrl.open_app("gedit")
```

### Combined (Browser + Desktop)

```python
from src.chrome_session_display0 import get_ctrl, reset
from src.desktop_controller import DesktopController

# Browser
browser = get_ctrl()
reset("https://example.com")

# Desktop
desktop = DesktopController()
desktop.screenshot("/tmp/before.png")
desktop.click(960, 540)
desktop.screenshot("/tmp/after.png")
```

## Components

### Browser (src/cdp_typer.py)
- Chrome DevTools Protocol implementation
- 950+ lines, fully typed
- Full API reference in SKILL.md

### Desktop (src/desktop_controller.py)
- Screenshot capture via gnome-screenshot
- Mouse input via pyatspi
- Keyboard input via ydotool
- App launching via subprocess

### Verification (src/verify_helpers.py)
- MD5 hashing for change detection
- DOM queries
- URL verification
- File verification

## Requirements

### System
- Linux (Ubuntu/Debian tested)
- GNOME desktop
- X11 or Wayland

### Tools
- gnome-screenshot (screenshot capture)
- python3-pyatspi (mouse input)
- ydotool (keyboard input)
- google-chrome or chromium (browser)

### Python
- Python 3.9+
- requests
- websocket-client
- pillow (optional, for image processing)

## Architecture

```
┌─────────────────────────────┐
│   Your Automation Script    │
└──────────────┬──────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼────┐ ┌──▼────┐ ┌───▼────┐
│Browser │ │Desktop│ │Verify  │
│ (CDP)  │ │(Input)│ │(Hash)  │
└───┬────┘ └───┬───┘ └───┬────┘
    │          │         │
    └──────────┴─────────┘
           │
    ┌──────▼──────────┐
    │  Real System    │
    │ Chrome/Desktop  │
    └─────────────────┘
```

## Performance

| Operation | Time |
|-----------|------|
| gnome-screenshot | 500-800ms |
| type_text | 250ms |
| key press | 100ms |
| click | 100ms |
| Chrome navigate | 2-3s |

## Limitations

- **Wayland + VirtualBox:** Mouse cursor doesn't visually move (cosmetic only, clicks still work)
- **Headless desktop:** xdotool doesn't work (use ydotool instead)
- **Browser:** Requires Chrome/Chromium installed

## Testing

Run the test suite:

```bash
python3 tests/run_all_desktop_tests.py
```

Tests verify:
- Real desktop screenshots (569KB+)
- Mouse click injection
- Keyboard input via ydotool
- Desktop app launching

## Security

- ✅ No API keys in code
- ✅ No credentials in repository
- ✅ Comprehensive `.gitignore`
- ✅ Safe subprocess usage

## License

MIT

## Author

Nima (@Eksjsjsidi)

## Repository

https://github.com/nimaansari/UI-agent

## Support

For issues, questions, or contributions:
1. Check SKILL.md for API reference
2. Check docs/ for deployment guides
3. Run tests to verify setup
4. Open GitHub issue for bugs
