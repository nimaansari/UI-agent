#!/bin/bash
# start_vnc.sh — starts x11vnc on :0 with Wayland/Xwayland support

DISPLAY_NUM=":0"
UID_NUM=$(id -u)

# Find XAUTHORITY automatically
XAUTH_FILE=""
for f in /run/user/$UID_NUM/*; do
 if [[ "$f" == *"Xwaylandauth"* ]] || [[ "$f" == *"mutter"* ]]; then
 XAUTH_FILE="$f"
 break
 fi
done

if [ -z "$XAUTH_FILE" ]; then
 XAUTH_FILE="$HOME/.Xauthority"
fi

echo "DISPLAY : $DISPLAY_NUM"
echo "XAUTHORITY : $XAUTH_FILE"

# Kill any existing x11vnc
pkill -f "x11vnc" 2>/dev/null
sleep 1

# Start x11vnc
x11vnc \
 -display $DISPLAY_NUM \
 -auth "$XAUTH_FILE" \
 -forever \
 -nopw \
 -bg \
 -noxdamage \
 -noxfixes \
 -nosel \
 -nosetclipboard \
 -rfbport 5900 \
 -xkb \
 -quiet

sleep 1

# Verify
if pgrep -f "x11vnc" > /dev/null; then
 echo "✅ x11vnc started on port 5900"
 echo " View desktop: xtightvncviewer localhost:5900"
 echo " UIAgent will use VNC for input injection"
else
 echo "❌ x11vnc failed to start"
 echo " Try manually: x11vnc -display :0 -auth $XAUTH_FILE -forever -nopw"
fi
