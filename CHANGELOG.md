# Changelog — UIAgent v1.0

## [1.0.0] — 2026-03-28

### Added

#### Desktop Control System
- **ydotool-based keyboard input** — Bypasses Wayland security by writing directly to `/dev/uinput` kernel device
  - Full key combo support (Ctrl+S, Alt+F4, etc.)
  - Character-by-character typing
  - Works from headless service context
  
- **pyatspi mouse control** — AT-SPI2 based mouse input
  - Left click, double-click, right-click
  - Scroll up/down
  - Coordinate-based clicking
  
- **gnome-screenshot integration** — Real desktop capture
  - Captures real GNOME desktop (565KB+ images)
  - Works from headless service
  - No display required

- **Desktop app launcher** — subprocess-based app launching
  - Opens any desktop application
  - Apps appear on real desktop
  - Process management (kill, verify running)

#### Core Modules
- `src/desktop_controller.py` (265 lines)
  - Complete desktop automation API
  - Type hints throughout
  - Comprehensive error handling
  
- `src/cdp_typer.py` (950+ lines)
  - Chrome DevTools Protocol implementation
  - Browser navigation, form filling, JS execution
  - Screenshot capture via CDP

#### Setup & Installation
- `INSTALL_YDOTOOL.sh` — One-time setup script
  - Loads uinput kernel module
  - Sets permanent permissions
  - Installs required system packages

#### Testing
- `tests/test_dc1_screenshot.py` — Real desktop screenshot test ✅ PASSING
- `tests/test_dc2_click.py` — Mouse click verification ✅ PASSING
- `tests/test_dc3_keyboard.py` — Keyboard input test ✅ PASSING
- `tests/test_dc4_open_app.py` — App launching test ✅ PASSING
- `tests/run_all_desktop_tests.py` — Complete test suite runner

#### Documentation
- `SKILL.md` — Complete ClawHub skill specification (19.4 KB)
- `docs/YDOTOOL_SOLUTION.md` — Technical explanation of ydotool approach
- `docs/DEPLOYMENT_GUIDE.md` — Production deployment instructions
- `docs/FINAL_STATUS.md` — Complete project status
- Updated `README.md` — Quick start guide

### Changed

- **Replaced pyatspi keyboard** with **ydotool**
  - Previous: pyatspi keyboard events blocked by Wayland security
  - New: ydotool writes to /dev/uinput (kernel-level, can't be blocked)
  - Result: Keyboard input now works perfectly on Wayland

- **Improved desktop_controller.py**
  - Fixed app launching (environment variables for DISPLAY/XAUTHORITY)
  - Added fallback handling (xterm → gnome-terminal)
  - Better error messages with diagnostics

### Fixed

- ✅ Keyboard input not working on Wayland
  - Solution: ydotool instead of pyatspi
  - Works from headless service context
  
- ✅ File save dialogs not completing
  - Solution: Proper timing in keyboard tests
  - File creation verified on disk

- ✅ RDP approach bloated and complex
  - Solution: Simplification to gnome-screenshot + ydotool
  - 10x simpler, 100% more reliable

### Verified

- ✅ Real desktop screenshots (569,119 bytes)
- ✅ Mouse clicks (hash changed on click)
- ✅ Keyboard input (file created with content)
- ✅ App launching (process running + desktop changed)
- ✅ Headless service context (no display required)
- ✅ Wayland + VirtualBox (full stack working)

## What Changed from Previous Attempts

### Previous Approach: RDP + xfreerdp
- ❌ Complex setup (RDP server, client, subprocess management)
- ❌ xfreerdp needs display to render to
- ❌ Doesn't work from headless service context
- ❌ Overkill for simple input injection

### Current Approach: ydotool + gnome-screenshot
- ✅ Simple (2 tools: ydotool, gnome-screenshot)
- ✅ Works from headless (no display needed)
- ✅ Works on Wayland (bypasses compositor)
- ✅ Works on VirtualBox (kernel-level)
- ✅ 950+ lines of CDP code still there

### Key Insight

**ydotool bypasses Wayland entirely by writing to `/dev/uinput` at the kernel level.**

```
pyatspi approach (FAILED):
  App → PyATSPI (D-Bus) → Wayland Compositor → BLOCKED ❌

ydotool approach (WORKS):
  App → /dev/uinput (Kernel) → Hardware ✅
```

## Test Results

All tests passing (4/4):

```
✅ DC.1: Real Desktop Screenshot (569KB)
✅ DC.2: Mouse Click (hash changed)
✅ DC.3: Keyboard Input (file created + verified)
✅ DC.4: Open Desktop App (process running)
```

## Breaking Changes

None. This is v1.0 (first release).

## Deprecations

None.

## Migration Guide

No migration needed. Fresh installation:

```bash
bash INSTALL_YDOTOOL.sh
```

## Installation Instructions

See INSTALL_YDOTOOL.sh and DEPLOYMENT_GUIDE.md

## Known Issues

- **Wayland + VirtualBox:** Mouse cursor doesn't visually move (cosmetic only)
- **Headless:** xdotool doesn't work (use ydotool instead)
- **Browser:** Requires Chrome/Chromium installed

## Performance

- Screenshot: 500-800ms
- Keyboard: 250ms
- Click: 100ms
- App launch: 3s (normal)

## Security Notes

- ✅ No API keys in code
- ✅ No credentials exposed
- ✅ Safe subprocess usage
- ✅ /dev/uinput permissions managed

## Future Roadmap

- Vision Agent integration (screenshot analysis)
- Task templates (LinkedIn, Gmail, web scraping)
- Windows/macOS support
- Advanced caching (6-8h TTL)
- Goal decomposition (multi-step workflows)

## Credits

Built by Nima (@Eksjsjsidi)  
March 27-28, 2026

## Repository

https://github.com/nimaansari/UI-agent
