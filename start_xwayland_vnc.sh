#!/bin/bash
# start_xwayland_vnc.sh
# Connects x11vnc to Xwayland display (X11 inside Wayland)

UID_NUM=$(id -u)
RUN_USER="/run/user/$UID_NUM"

echo "=== Finding Xwayland auth ==="

# Find auth file
AUTH_FILE=""
DISPLAY_NUM=":0"

for f in $RUN_USER/.mutter-Xwaylandauth.* $RUN_USER/*Xwaylandauth*; do
 if [ -f "$f" ]; then
 AUTH_FILE="$f"
 echo " Auth file: $(basename $f)"
 break
 fi
done

if [ -z "$AUTH_FILE" ]; then
 # Try standard XAUTHORITY
 if [ -f "$HOME/.Xauthority" ]; then
 AUTH_FILE="$HOME/.Xauthority"
 echo " Using: $HOME/.Xauthority"
 else
 echo "❌ No auth file found"
 exit 1
 fi
fi

# Find Xwayland display number
XWAYLAND_DISPLAY=$(pgrep -a Xwayland 2>/dev/null \
 | grep -oP ':\d+' | head -1)

if [ -n "$XWAYLAND_DISPLAY" ]; then
 DISPLAY_NUM=$XWAYLAND_DISPLAY
 echo " Xwayland display: $DISPLAY_NUM"
else
 echo " Using default display: $DISPLAY_NUM"
fi

echo ""
echo "=== Testing X11 connection to Xwayland ==="
DISPLAY=$DISPLAY_NUM XAUTHORITY=$AUTH_FILE xdpyinfo > /dev/null 2>&1
if [ $? -eq 0 ]; then
 echo "✅ X11 connection works on $DISPLAY_NUM"
else
 echo "❌ X11 connection failed"
 echo " DISPLAY=$DISPLAY_NUM"
 echo " XAUTHORITY=$AUTH_FILE"
 exit 1
fi

echo ""
echo "=== Starting x11vnc on Xwayland ==="

pkill -f x11vnc 2>/dev/null
sleep 1

x11vnc \
 -display $DISPLAY_NUM \
 -auth "$AUTH_FILE" \
 -forever \
 -nopw \
 -bg \
 -rfbport 5900 \
 -xkb \
 -noxdamage \
 -noxfixes \
 -nosel \
 -nosetclipboard \
 -quiet

sleep 2

if pgrep -f x11vnc > /dev/null; then
 echo "✅ x11vnc started on Xwayland!"
 echo " Display    : $DISPLAY_NUM"
 echo " Auth       : $(basename $AUTH_FILE)"
 echo " Port 5900  : open"
 echo ""
 echo "Connect: xtightvncviewer localhost:5900"
else
 echo "❌ x11vnc failed to start"
fi
