#!/bin/bash
# INSTALL_YDOTOOL.sh
# One-time setup for ydotool + uinput

set -e

echo "========================================"
echo "UIAgent ydotool + uinput Setup"
echo "========================================"

# Step 1: Load uinput kernel module
echo ""
echo "[1] Loading uinput kernel module..."
sudo modprobe uinput
sudo chmod 666 /dev/uinput
echo "✅ uinput loaded"

# Step 2: Permanent boot loading
echo ""
echo "[2] Setting up permanent loading..."
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf > /dev/null
echo "✅ /etc/modules-load.d/uinput.conf created"

# Step 3: Permanent permissions
echo ""
echo "[3] Setting up permanent permissions..."
echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null
sudo udevadm control --reload-rules
echo "✅ /etc/udev/rules.d/99-uinput.rules created"

# Step 4: Install tools
echo ""
echo "[4] Installing tools..."
sudo apt-get update
sudo apt-get install -y gnome-screenshot python3-pyatspi ydotool
echo "✅ Tools installed"

# Step 5: Verify
echo ""
echo "[5] Verifying installation..."

if [ -c /dev/uinput ]; then
    echo "✅ /dev/uinput exists"
else
    echo "❌ /dev/uinput not found"
    exit 1
fi

if command -v gnome-screenshot &> /dev/null; then
    echo "✅ gnome-screenshot installed"
else
    echo "❌ gnome-screenshot not found"
    exit 1
fi

if command -v ydotool &> /dev/null; then
    echo "✅ ydotool installed"
else
    echo "❌ ydotool not found"
    exit 1
fi

if python3 -c "import pyatspi" 2>/dev/null; then
    echo "✅ pyatspi installed"
else
    echo "❌ pyatspi not found"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "All tools ready. Test with:"
echo "  python3 tests/test_dc4_keyboard.py"
