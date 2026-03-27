#!/bin/bash
# start_wayvnc.sh — Start wayvnc on Wayland desktop

# Kill existing wayvnc
pkill -f wayvnc 2>/dev/null
sleep 1

# Find output name (optional)
OUTPUT=$(wayvnc --list-outputs 2>/dev/null | head -1 | awk '{print $1}')
if [ -z "$OUTPUT" ]; then
 OUTPUT=""
fi

echo "Starting wayvnc on port 5900..."
if [ -n "$OUTPUT" ]; then
 echo " Output: $OUTPUT"
 wayvnc --output="$OUTPUT" 0.0.0.0 5900 &
else
 wayvnc 0.0.0.0 5900 &
fi

sleep 2

if pgrep -f wayvnc > /dev/null; then
 echo "✅ wayvnc started on port 5900"
 echo " Connect: xtightvncviewer localhost:5900"
else
 echo "❌ wayvnc failed to start"
 echo " Try: wayvnc 0.0.0.0 5900"
fi
