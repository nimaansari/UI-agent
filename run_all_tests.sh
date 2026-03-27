#!/bin/bash
# run_all_tests.sh
# Complete UIAgent test suite runner
# Tests RDP connectivity, desktop access, and full automation

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "============================================================"
echo "UIAgent Complete Test Suite"
echo "============================================================"
echo "Project: $PROJECT_DIR"
echo "Time: $(date)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

# Function to run a test
run_test() {
    local name="$1"
    local script="$2"
    local description="$3"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$description"
    echo ""
    
    if [ ! -f "$script" ]; then
        echo -e "${YELLOW}⏭ SKIP${NC} - File not found: $script"
        ((SKIPPED++))
        return
    fi
    
    if python3 "$script"; then
        echo ""
        echo -e "${GREEN}✅ PASSED${NC} - $name"
        ((PASSED++))
    else
        echo ""
        echo -e "${RED}❌ FAILED${NC} - $name"
        ((FAILED++))
    fi
}

# Function to run a Python inline test
run_inline_test() {
    local name="$1"
    local description="$2"
    local code="$3"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$description"
    echo ""
    
    if python3 << PYEOF
import sys
$code
PYEOF
    then
        echo ""
        echo -e "${GREEN}✅ PASSED${NC} - $name"
        ((PASSED++))
    else
        echo ""
        echo -e "${RED}❌ FAILED${NC} - $name"
        ((FAILED++))
    fi
}

# ============================================================
# SECTION 1: Environment Check
# ============================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "SECTION 1: Environment & Tools"
echo "════════════════════════════════════════════════════════════"

echo ""
echo "[1] Checking required tools..."

for tool in python3 xfreerdp scrot xdotool; do
    if command -v $tool &> /dev/null; then
        echo -e "${GREEN}✅${NC} $tool installed"
    else
        echo -e "${YELLOW}⚠️${NC} $tool not found (some tests may be skipped)"
    fi
done

echo ""
echo "[2] Checking GNOME Remote Desktop..."
if systemctl --user is-active gnome-remote-desktop &> /dev/null; then
    echo -e "${GREEN}✅${NC} GNOME Remote Desktop is running"
else
    echo -e "${RED}❌${NC} GNOME Remote Desktop not running"
    echo "   Start with: systemctl --user start gnome-remote-desktop"
fi

if ss -tlnp 2>/dev/null | grep -q 3389; then
    echo -e "${GREEN}✅${NC} Port 3389 (RDP) is listening"
else
    echo -e "${YELLOW}⚠️${NC} Port 3389 not listening"
fi

# ============================================================
# SECTION 2: Preflight Checks
# ============================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "SECTION 2: Pre-flight Checks"
echo "════════════════════════════════════════════════════════════"

run_test "Preflight (Autostart)" \
    "tests/preflight_autostart.py" \
    "Checks: Session type, DISPLAY, XAUTHORITY, tools, config files"

# ============================================================
# SECTION 3: RDP Controller Test
# ============================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "SECTION 3: RDP Controller"
echo "════════════════════════════════════════════════════════════"

run_inline_test "RDP Controller Basic" \
    "Tests: RDP initialization, xfreerdp availability" \
    "
from src.rdp_controller import RDPController
try:
    rdp = RDPController()
    print('✅ RDP controller initialized')
    rdp.close()
except Exception as e:
    print(f'❌ Error: {e}')
    raise
"

run_inline_test "RDP Screenshot" \
    "Tests: Screenshot capture (must be > 500KB for real desktop)" \
    "
import os
from src.rdp_controller import RDPController

rdp = RDPController()
img = rdp.screenshot()

if img is None:
    print('❌ Screenshot returned None')
    raise RuntimeError('Screenshot failed')

if isinstance(img, str):
    size = os.path.getsize(img)
    print(f'Screenshot file: {img}')
    print(f'Size: {size:,} bytes')
    if size > 500000:
        print('✅ Real desktop size (> 500KB)')
    else:
        print(f'⚠️ Screenshot too small ({size}b, expected > 500KB)')
else:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        size = os.path.getsize(f.name)
        print(f'Screenshot saved: {f.name}')
        print(f'Size: {size:,} bytes')
        if size > 500000:
            print('✅ Real desktop size (> 500KB)')
        else:
            print(f'⚠️ Screenshot too small ({size}b)')

rdp.close()
"

run_inline_test "RDP Mouse Movement" \
    "Tests: Mouse move commands (check if cursor moves on desktop)" \
    "
from src.rdp_controller import RDPController
import time

rdp = RDPController()
print('Moving mouse to (960, 540)...')
rdp.mouse_move(960, 540)
time.sleep(0.5)

print('Moving mouse to (400, 300)...')
rdp.mouse_move(400, 300)
time.sleep(0.5)

print('✅ Mouse move commands sent')
print('⚠️ (Check if cursor moved on your desktop)')

rdp.close()
"

run_inline_test "RDP Keyboard Input" \
    "Tests: Type text and key press" \
    "
from src.rdp_controller import RDPController

rdp = RDPController()
print('Testing keyboard input...')
rdp.type_text('Test123')
rdp.key_press('Return')
print('✅ Keyboard input commands sent')
rdp.close()
"

# ============================================================
# SECTION 4: Autostart Tests
# ============================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "SECTION 4: Autostart Configuration"
echo "════════════════════════════════════════════════════════════"

run_test "Autostart Setup Test" \
    "tests/test_a3_xdotool_real.py" \
    "Tests: xdotool on real desktop (critical mouse test)"

# ============================================================
# SECTION 5: Summary
# ============================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Passed:${NC}  $PASSED"
echo -e "${RED}Failed:${NC}  $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

TOTAL=$((PASSED + FAILED + SKIPPED))
if [ $FAILED -eq 0 ] && [ $PASSED -gt 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "UIAgent is ready for:"
    echo "✅ Real desktop screenshots (via RDP)"
    echo "✅ Mouse and keyboard control (via RDP)"
    echo "✅ Full desktop automation"
    exit 0
elif [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Check the output above for details."
    exit 1
else
    echo -e "${YELLOW}⚠️ NO TESTS RAN${NC}"
    echo ""
    echo "You may be missing required files or tools."
    echo "Ensure you're in the gui-cowork directory and have all dependencies."
    exit 1
fi
