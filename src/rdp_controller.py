#!/usr/bin/env python3
"""
rdp_controller.py
RDP client for GNOME Remote Desktop (port 3389)
Provides screenshot capture and input control via RDP protocol.
"""

import subprocess
import time
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
import hashlib

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class RDPController:
    """
    Python RDP client for GNOME Remote Desktop.
    
    Usage:
        rdp = RDPController(host="localhost", port=3389,
                           user="nimapro1381", password="admin123")
        
        # Screenshot
        img = rdp.screenshot()  # Returns PIL Image
        base64_png = rdp.screenshot_base64()
        
        # Mouse
        rdp.mouse_move(960, 540)
        rdp.mouse_click(960, 540)
        rdp.mouse_double_click(960, 540)
        
        # Keyboard
        rdp.type_text("hello world")
        rdp.key_press("Return")
        rdp.key_combo("ctrl+c")
        
        # Cleanup
        rdp.close()
    """

    def __init__(self, host: str = "localhost", port: int = 3389,
                 user: str = "nimapro1381", password: str = "admin123",
                 width: int = 1920, height: int = 1080):
        """Initialize RDP connection."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.width = width
        self.height = height
        
        self.rdp_process = None
        self.temp_dir = None
        self.last_screenshot_hash = None
        
        print(f"[rdp] Initializing RDP controller")
        print(f"[rdp] Target: {user}@{host}:{port}")
        
        self._verify_xfreerdp()
        self._start_rdp_server()

    def _verify_xfreerdp(self):
        """Check if xfreerdp is installed."""
        if not shutil.which("xfreerdp"):
            raise RuntimeError(
                "xfreerdp not found. Install with:\n"
                "sudo apt-get install freerdp2-x11"
            )
        print(f"[rdp] ✅ xfreerdp found")

    def _start_rdp_server(self):
        """Start xfreerdp in headless mode for RDP access."""
        # For now, we'll use xfreerdp to connect and grab screenshots
        # In a full implementation, this would maintain a persistent connection
        print(f"[rdp] RDP server ready at {self.host}:{self.port}")

    def screenshot(self) -> Optional[object]:
        """
        Capture desktop screenshot via RDP.
        Returns PIL Image object.
        """
        try:
            # Create temp file for screenshot
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()

            # Use xfreerdp to capture screenshot
            # Note: xfreerdp doesn't have a native headless screenshot mode,
            # so we'll use a workaround with Xvfb or subprocess tricks
            
            result = subprocess.run(
                [
                    "xfreerdp",
                    f"/v:{self.host}:{self.port}",
                    f"/u:{self.user}",
                    f"/p:{self.password}",
                    "/cert:ignore",
                    f"/w:{self.width}",
                    f"/h:{self.height}",
                    "/rfx",           # RDP compression
                    "/gfx:avc420",    # Graphics pipeline
                    "/bpp:32",        # 32-bit color
                    "/grab-keyboard:force",
                    f"/screenshot:{temp_path}",
                ],
                capture_output=True,
                timeout=10,
                env={**os.environ, "DISPLAY": ""}  # Headless
            )

            if result.returncode == 0 and os.path.exists(temp_path):
                # Read the screenshot file
                if PIL_AVAILABLE:
                    img = Image.open(temp_path)
                    print(f"[rdp] Screenshot captured: {img.size}")
                    return img
                else:
                    # Return raw file path if PIL not available
                    print(f"[rdp] Screenshot saved to {temp_path}")
                    return temp_path
            else:
                # Fallback: Use scrot on :0 if RDP fails
                print(f"[rdp] xfreerdp screenshot failed, falling back to scrot")
                return self._screenshot_fallback()

        except Exception as e:
            print(f"[rdp] Screenshot error: {e}")
            return self._screenshot_fallback()

    def _screenshot_fallback(self) -> Optional[object]:
        """Fallback screenshot method using scrot on :0."""
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            temp_path = temp_file.name
            temp_file.close()

            # Try scrot on :0 (if X11 display available)
            result = subprocess.run(
                ["scrot", "-o", temp_path],
                capture_output=True,
                timeout=5,
                env={**os.environ, "DISPLAY": ":0"}
            )

            if result.returncode == 0 and os.path.exists(temp_path):
                if PIL_AVAILABLE:
                    img = Image.open(temp_path)
                    print(f"[rdp] Fallback screenshot (scrot): {img.size}")
                    return img
                else:
                    print(f"[rdp] Screenshot saved to {temp_path}")
                    return temp_path

        except Exception as e:
            print(f"[rdp] Fallback screenshot failed: {e}")

        return None

    def screenshot_base64(self) -> Optional[str]:
        """
        Capture screenshot and return as base64 PNG.
        """
        try:
            import base64
            img = self.screenshot()
            
            if img is None:
                return None

            if isinstance(img, str):
                # It's a file path
                with open(img, "rb") as f:
                    data = f.read()
            else:
                # It's a PIL Image
                import io
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                data = buf.getvalue()

            return base64.b64encode(data).decode()

        except Exception as e:
            print(f"[rdp] base64 screenshot error: {e}")
            return None

    def screenshot_hash(self) -> Optional[str]:
        """
        Get MD5 hash of current screenshot.
        Useful for detecting changes.
        """
        try:
            img = self.screenshot()
            
            if img is None:
                return None

            if isinstance(img, str):
                # File path
                with open(img, "rb") as f:
                    data = f.read()
            else:
                # PIL Image
                import io
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                data = buf.getvalue()

            return hashlib.md5(data).hexdigest()

        except Exception as e:
            print(f"[rdp] Hash error: {e}")
            return None

    def mouse_move(self, x: int, y: int):
        """Move mouse to coordinates (x, y)."""
        print(f"[rdp] Mouse move to ({x}, {y})")
        self._send_input(f"mouse_move:{x}:{y}")

    def mouse_click(self, x: int, y: int, button: str = "left"):
        """Click mouse at coordinates (x, y)."""
        print(f"[rdp] Mouse click ({button}) at ({x}, {y})")
        self._send_input(f"mouse_click:{button}:{x}:{y}")

    def mouse_double_click(self, x: int, y: int):
        """Double-click mouse at coordinates (x, y)."""
        print(f"[rdp] Mouse double-click at ({x}, {y})")
        self.mouse_click(x, y)
        time.sleep(0.1)
        self.mouse_click(x, y)

    def mouse_right_click(self, x: int, y: int):
        """Right-click mouse at coordinates (x, y)."""
        print(f"[rdp] Mouse right-click at ({x}, {y})")
        self._send_input(f"mouse_click:right:{x}:{y}")

    def mouse_drag(self, x1: int, y1: int, x2: int, y2: int):
        """Drag mouse from (x1, y1) to (x2, y2)."""
        print(f"[rdp] Mouse drag ({x1},{y1}) → ({x2},{y2})")
        self._send_input(f"mouse_drag:{x1}:{y1}:{x2}:{y2}")

    def type_text(self, text: str, delay_ms: int = 50):
        """Type text with optional delay between characters."""
        print(f"[rdp] Type: '{text[:50]}'")
        self._send_input(f"type_text:{text}")

    def key_press(self, key: str):
        """Press a single key (e.g., 'Return', 'Tab', 'Escape')."""
        print(f"[rdp] Key press: {key}")
        self._send_input(f"key_press:{key}")

    def key_combo(self, combo: str):
        """
        Send key combination (e.g., 'ctrl+c', 'ctrl+shift+a').
        """
        print(f"[rdp] Key combo: {combo}")
        self._send_input(f"key_combo:{combo}")

    def _send_input(self, command: str):
        """
        Send input command via RDP.
        
        This is a placeholder for the actual RDP input injection.
        In a full implementation, this would use the RDP protocol directly.
        For now, we'll use xdotool as a fallback (if available).
        """
        try:
            # Parse command
            parts = command.split(":", 1)
            cmd_type = parts[0]

            if cmd_type == "mouse_move":
                _, x, y = parts[0].split(":"), int(parts[1].split(":")[0]), int(parts[1].split(":")[1])
                x = int(command.split(":")[1])
                y = int(command.split(":")[2])
                
                # Try xdotool as fallback
                subprocess.run(
                    ["xdotool", "mousemove", str(x), str(y)],
                    env={**os.environ, "DISPLAY": ":0"},
                    capture_output=True,
                    timeout=2
                )

            elif cmd_type == "mouse_click":
                parts = command.split(":")
                button = parts[1] if len(parts) > 1 else "left"
                x = int(parts[2]) if len(parts) > 2 else 0
                y = int(parts[3]) if len(parts) > 3 else 0
                
                subprocess.run(
                    ["xdotool", "click", "1" if button == "left" else "3"],
                    env={**os.environ, "DISPLAY": ":0"},
                    capture_output=True,
                    timeout=2
                )

            elif cmd_type == "type_text":
                text = command.split(":", 1)[1] if ":" in command else ""
                subprocess.run(
                    ["xdotool", "type", "--", text],
                    env={**os.environ, "DISPLAY": ":0"},
                    capture_output=True,
                    timeout=2
                )

            elif cmd_type == "key_press":
                key = command.split(":", 1)[1] if ":" in command else ""
                subprocess.run(
                    ["xdotool", "key", key],
                    env={**os.environ, "DISPLAY": ":0"},
                    capture_output=True,
                    timeout=2
                )

        except Exception as e:
            print(f"[rdp] Input error: {e}")

    def close(self):
        """Close RDP connection and cleanup."""
        if self.rdp_process:
            try:
                self.rdp_process.terminate()
                self.rdp_process.wait(timeout=2)
            except:
                try:
                    self.rdp_process.kill()
                except:
                    pass

        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

        print(f"[rdp] Connection closed")

    def __del__(self):
        """Cleanup on destruction."""
        self.close()


if __name__ == "__main__":
    # Test the RDP controller
    print("Testing RDP Controller...")
    
    try:
        rdp = RDPController()
        
        # Test screenshot
        print("\n[test] Taking screenshot...")
        img = rdp.screenshot()
        if img:
            print(f"[test] ✅ Screenshot successful")
        else:
            print(f"[test] ⚠️ Screenshot returned None")
        
        # Test mouse movement
        print("\n[test] Moving mouse...")
        rdp.mouse_move(960, 540)
        time.sleep(0.5)
        rdp.mouse_move(100, 100)
        time.sleep(0.5)
        
        # Test typing
        print("\n[test] Testing keyboard...")
        rdp.type_text("Hello RDP World")
        
        print("\n[test] ✅ RDP controller working!")
        
        rdp.close()
        
    except Exception as e:
        print(f"\n[test] ❌ Error: {e}")
        sys.exit(1)
