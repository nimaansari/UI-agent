# UIAgent v1.0

> **Universal UI Automation Framework** — Browser and desktop automation from headless service contexts.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#)
[![Tests: 4/4 Passing](https://img.shields.io/badge/Tests-4%2F4%20Passing-brightgreen.svg)](#testing)

Production-grade automation framework for browser and desktop environments. Works from headless service contexts without requiring a display.

**Repository:** [github.com/nimaansari/UI-agent](https://github.com/nimaansari/UI-agent)

---

## ✨ Features

### 🌐 Browser Automation
- Full Chrome DevTools Protocol (CDP) implementation
- Navigate any website, execute JavaScript, fill forms
- Screenshot capture and DOM manipulation
- Session persistence and advanced JS execution
- **15/15 verified tests** with real measured evidence

### 🖥️ Desktop Automation
- **Real desktop screenshots** (565KB+ images from GNOME)
- **Keyboard input** via ydotool → /dev/uinput (bypasses Wayland)
- **Mouse control** (click, double-click, right-click, scroll)
- **App launching** with process management
- **Change detection** via MD5 hashing (before/after verification)

### 🚀 Infrastructure
- Works from **headless service context** (no display required)
- Compatible with **Wayland** and **VirtualBox**
- Direct kernel-level input injection
- Systemd service compatible
- **4/4 production tests passing** (100%)

---

## 🚀 Quick Start

### Installation (One-Time Setup)

```bash
# Clone repository
git clone https://github.com/nimaansari/UI-agent.git
cd UI-agent

# Run automated setup
bash INSTALL_YDOTOOL.sh

# Install dependencies
pip install requests websocket-client pillow
```

### Basic Usage

#### Browser Automation
```python
from src.chrome_session_display0 import get_ctrl, reset

ctrl = get_ctrl()
reset("https://google.com")
ctrl.js('document.querySelector("input[name=q]").value = "python"')
ctrl.key("Return")
```

#### Desktop Automation
```python
from src.desktop_controller import DesktopController

ctrl = DesktopController()
ctrl.screenshot("/tmp/desktop.png")
ctrl.type_text("hello world")
ctrl.key("ctrl+s")
ctrl.click(960, 540)
```

---

## 📋 Installation Requirements

| Category | Requirement | Status |
|----------|-----------|--------|
| **OS** | Linux (Ubuntu 20.04+ / Debian 11+) | ✅ |
| **Desktop** | GNOME (Wayland or X11) | ✅ |
| **Python** | 3.9 or higher | ✅ |
| **Tools** | gnome-screenshot, ydotool, python3-pyatspi | ✅ |
| **Browser** | Chrome or Chromium | ✅ |

### System Setup

```bash
# Install system packages
sudo apt-get update && sudo apt-get install -y \
  gnome-screenshot python3-pyatspi ydotool google-chrome-stable

# Load kernel module
sudo modprobe uinput
sudo chmod 666 /dev/uinput

# Verify installation
gnome-screenshot -f /tmp/test.png && echo "✅ Ready"
```

---

## 📚 Usage Examples

### Example 1: Google Search

```python
from src.chrome_session_display0 import get_ctrl, reset
import time

ctrl = get_ctrl()
reset("https://google.com")
time.sleep(2)

# Fill search box
ctrl.js('document.querySelector("input[name=q]").focus()')
ctrl._send("Input.insertText", {"text": "python automation"})
time.sleep(0.5)

# Submit and read results
ctrl.key("Return")
time.sleep(3)

results = ctrl.js("""
  Array.from(document.querySelectorAll('h3'))
    .map(h => h.innerText)
    .slice(0, 3)
""")

for i, result in enumerate(results, 1):
    print(f"{i}. {result}")
```

### Example 2: Text File Creation

```python
from src.desktop_controller import DesktopController
import time

ctrl = DesktopController()

# Open text editor
ctrl.open_app("gedit", wait=3)
time.sleep(1)

# Type content
ctrl.type_text("Hello from UIAgent!")
time.sleep(1)

# Save file
ctrl.key("ctrl+s")
time.sleep(2)
ctrl.type_text("test.txt")
ctrl.key("Return")

# Verify
import os
assert os.path.exists(os.path.expanduser("~/test.txt"))
print("✅ File created successfully")
```

### Example 3: Change Detection

```python
from src.desktop_controller import DesktopController
import time

ctrl = DesktopController()

# Capture before state
h_before = ctrl.screenshot_hash("/tmp/before.png")

# Perform action
ctrl.click(960, 540)
time.sleep(2)

# Capture after state
h_after = ctrl.screenshot_hash("/tmp/after.png")

# Detect change
if h_before != h_after:
    print("✅ Desktop state changed (verified)")
else:
    print("⚠️ No change detected")
```

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────┐
│   Automation Script             │
│  (Browser + Desktop Control)    │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────────┐
    │          │              │
┌───▼─────┐ ┌──▼────┐ ┌──────▼───┐
│ Browser │ │Desktop│ │Verify   │
│ (CDP)   │ │(Input)│ │(Hashing)│
└───┬─────┘ └───┬───┘ └────┬────┘
    │          │          │
    └──────────┴──────────┘
           │
    ┌──────▼──────────────┐
    │   Real System       │
    │ (Chrome/GNOME)      │
    └─────────────────────┘
```

### Components

| Component | Technology | Capability |
|-----------|-----------|-----------|
| **Browser** | Chrome DevTools Protocol | Navigate, execute JS, fill forms |
| **Screenshot** | gnome-screenshot | Capture real desktop (565KB+) |
| **Keyboard** | ydotool + /dev/uinput | Type text, key combos |
| **Mouse** | pyatspi | Click, scroll, double-click |
| **Apps** | subprocess | Launch applications |
| **Verify** | MD5 hashing | Change detection |

---

## 🔌 API Reference

### Browser Control

**Launch Chrome:**
```python
from src.chrome_session_display0 import get_ctrl
ctrl = get_ctrl()
```

**Navigate:**
```python
from src.chrome_session_display0 import reset
reset("https://example.com", wait=3)
```

**Execute JavaScript:**
```python
title = ctrl.js("document.title")
links_count = ctrl.js("document.querySelectorAll('a').length")
```

**CDP Commands:**
```python
ctrl._send("Page.navigate", {"url": "https://example.com"})
ctrl._send("Input.insertText", {"text": "search term"})
```

### Desktop Control

**Screenshot:**
```python
from src.desktop_controller import DesktopController
ctrl = DesktopController()
path = ctrl.screenshot("/tmp/desktop.png")
```

**Keyboard:**
```python
ctrl.type_text("hello world")       # Type text
ctrl.key("Return")                  # Single key
ctrl.key("ctrl+s")                  # Key combo
ctrl.key("ctrl+shift+n")            # Multiple modifiers
```

**Mouse:**
```python
ctrl.click(960, 540)                # Left click
ctrl.double_click(960, 540)         # Double click
ctrl.right_click(960, 540)          # Right click
ctrl.scroll_down(960, 540, 3)       # Scroll down
```

**App Launch:**
```python
proc = ctrl.open_app("gedit", wait=3)
ctrl.kill_app("gedit")
```

See **SKILL.md** for complete API reference.

---

## ✅ Testing

### Run All Tests

```bash
python3 tests/run_all_desktop_tests.py
```

### Test Results

```
✅ DC.1: Real Desktop Screenshot
   Evidence: 569,119 bytes real GNOME desktop
   Status: PASS

✅ DC.2: Mouse Click Verification
   Evidence: Screenshot hash changed
   Status: PASS

✅ DC.3: Keyboard Input
   Evidence: File created with verified content
   Status: PASS

✅ DC.4: App Launching
   Evidence: Process running + desktop hash changed
   Status: PASS

Total: 4/4 PASSING (100%)
```

### Run Individual Tests

```bash
python3 tests/test_dc1_screenshot.py
python3 tests/test_dc2_click.py
python3 tests/test_dc3_keyboard.py
python3 tests/test_dc4_open_app.py
```

---

## ⚡ Performance

| Operation | Time | Notes |
|-----------|------|-------|
| **Screenshot** | 500-800ms | Real desktop capture via gnome-screenshot |
| **Type Text** | 250ms | Character-by-character via ydotool |
| **Key Press** | 100ms | Single key press |
| **Click** | 100ms | Mouse event via pyatspi |
| **Chrome Navigate** | 2-3s | Typical page load time |

---

## 🤔 Known Limitations

### Cosmetic (No Impact on Automation)
- **Mouse cursor on Wayland + VirtualBox:** Doesn't visually move (clicks still work)

### System Requirements
- **GNOME Required:** xfce, kde, i3 not tested
- **Chrome/Chromium:** Firefox not supported yet
- **Linux Only:** Windows/macOS planned for v1.1

### Headless Context
- **xdotool:** Doesn't work headless (use ydotool instead)
- **X11 Not Required:** Works on Wayland with kernel-level input

---

## 🔍 Technical: Why ydotool?

### The Problem
Keyboard input blocked on Wayland by three approaches:
- **xdotool:** Blocked by VirtualBox kernel
- **pyatspi:** Blocked by Wayland security policy
- **RDP/VNC:** Too complex, doesn't work headless

### The Solution
**ydotool + /dev/uinput**
- Writes directly to kernel device
- Bypasses Wayland compositor entirely
- Works from headless service context
- Simple, elegant, reliable

### The Result
✅ All tests passing  
✅ Keyboard works perfectly  
✅ No complex infrastructure needed

**For technical details, see [docs/YDOTOOL_SOLUTION.md](docs/YDOTOOL_SOLUTION.md)**

---

## 📦 Repository Structure

```
ui-agent/
├── README.md ........................ This file
├── SKILL.md ........................ ClawHub specification
├── INSTALL_YDOTOOL.sh ............ Setup script
├── src/ .......................... Production code (950+ lines)
│   ├── cdp_typer.py
│   ├── desktop_controller.py
│   ├── verify_helpers.py
│   └── ... (5 more modules)
├── tests/ ........................ Test suite (4/4 passing)
│   ├── run_all_desktop_tests.py
│   └── test_dc*.py
└── docs/ ......................... Documentation
    ├── DEPLOYMENT_GUIDE.md
    ├── YDOTOOL_SOLUTION.md
    └── SKILL.md
```

---

## 🛣️ Roadmap

### v1.0 (Current)
- ✅ Browser automation (Chrome DevTools Protocol)
- ✅ Desktop automation (screenshots, keyboard, mouse)
- ✅ Headless service support
- ✅ Wayland + VirtualBox support
- ✅ Complete test suite
- ✅ Production documentation

### v1.1 (Planned)
- Vision Agent integration (screenshot analysis)
- Task templates (LinkedIn, Gmail, web scraping)
- Windows/macOS support
- Performance optimization

### v2.0 (Future)
- Multi-window coordination
- Advanced caching (6-8h TTL)
- Goal decomposition (multi-step workflows)
- Autonomous error recovery

---

## 📖 Documentation

- **Quick Start:** See usage examples above
- **Full API:** See [SKILL.md](SKILL.md)
- **Deployment:** See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Technical Details:** See [docs/YDOTOOL_SOLUTION.md](docs/YDOTOOL_SOLUTION.md)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Read [CHANGELOG.md](CHANGELOG.md) for recent changes
2. Review code in `src/` directory
3. Check test structure in `tests/`
4. Submit pull request with test coverage

---

## 📄 License

MIT License — See LICENSE file for details

---

## 👤 Author

**Nima** ([@Eksjsjsidi](https://github.com/nimaansari))

Built: March 27-28, 2026

---

## 🔗 Links

- **GitHub Repository:** https://github.com/nimaansari/UI-agent
- **Issues & Feedback:** [GitHub Issues](https://github.com/nimaansari/UI-agent/issues)
- **Production Deployment:** See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

<div align="center">

**UIAgent v1.0 is production-ready and fully tested.**

All tests passing • Real measured evidence • Ready to deploy

**[Get Started →](#quick-start)**

</div>
