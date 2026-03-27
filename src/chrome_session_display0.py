#!/usr/bin/env python3
"""
chrome_session_display0.py
Chrome session manager using :0 (real desktop).
User sees Chrome open live on their desktop.
"""

import os, time, glob, socket, subprocess, requests
from cdp_typer import CDPTyper

CDP_PORT = 9222
PROFILE = "/tmp/chrome-automation-profile"
_proc = None
_ctrl = None

CHROME_FLAGS = [
 f"--remote-debugging-port={CDP_PORT}",
 f"--user-data-dir={PROFILE}",
 "--no-sandbox",
 "--disable-gpu",
 "--disable-dev-shm-usage",
 "--no-first-run",
 "--no-default-browser-check",
 "--disable-extensions",
 "--disable-sync",
 "--disable-crash-reporter",
 "--disable-breakpad",
 "--dns-prefetch-disable",
 "--proxy-server=direct://",
 "--proxy-bypass-list=*",
 "--ignore-certificate-errors",
 "--disable-blink-features=AutomationControlled",
]


def _find_xauthority():
 uid = os.getuid()
 run_user = f"/run/user/{uid}"
 if os.path.isdir(run_user):
 for f in os.listdir(run_user):
 if "Xwaylandauth" in f or "mutter" in f.lower():
 return os.path.join(run_user, f)
 standard = os.path.expanduser("~/.Xauthority")
 if os.path.exists(standard):
 return standard
 return None


def _build_env():
 env = {}
 for key in ["PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL",
 "XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS"]:
 if key in os.environ:
 env[key] = os.environ[key]

 env["DISPLAY"] = ":0"
 env["GDK_BACKEND"] = "x11"
 env["QT_QPA_PLATFORM"] = "xcb"
 env.pop("WAYLAND_DISPLAY", None)

 xauth = _find_xauthority()
 if xauth:
 env["XAUTHORITY"] = xauth
 print(f"[session] XAUTHORITY: {xauth}")

 return env


def _port_is_free(port, timeout=15):
 start = time.time()
 free_count = 0
 while time.time() - start < timeout:
 try:
 s = socket.socket()
 s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 s.settimeout(0.3)
 s.connect(("127.0.0.1", port))
 s.close()
 free_count = 0
 time.sleep(0.3)
 except (ConnectionRefusedError, OSError):
 free_count += 1
 if free_count >= 2:
 return True
 time.sleep(0.3)
 raise TimeoutError(f"Port {port} still bound after {timeout}s")


def _port_is_ready(port, timeout=30):
 start = time.time()
 while time.time() - start < timeout:
 try:
 resp = requests.get(f"http://localhost:{port}/json", timeout=1)
 if resp.status_code == 200 and resp.json():
 return True
 except Exception:
 pass
 time.sleep(0.5)
 raise TimeoutError(f"CDP port {port} not ready after {timeout}s")


def _clean_locks():
 for f in [f"{PROFILE}/SingletonLock",
 f"{PROFILE}/SingletonCookie",
 f"{PROFILE}/SingletonSocket"]:
 if os.path.exists(f):
 try:
 os.remove(f)
 except OSError:
 pass


def get_ctrl():
 global _proc, _ctrl

 if _ctrl and _proc and _proc.poll() is None:
 try:
 requests.get(f"http://localhost:{CDP_PORT}/json", timeout=1)
 return _ctrl
 except Exception:
 pass

 subprocess.run(
 ["pkill", "-f", f"remote-debugging-port={CDP_PORT}"],
 capture_output=True
 )
 try:
 _port_is_free(CDP_PORT, timeout=10)
 except TimeoutError:
 subprocess.run(["fuser", "-k", f"{CDP_PORT}/tcp"], capture_output=True)
 time.sleep(2)

 _clean_locks()
 os.makedirs(PROFILE, exist_ok=True)

 env = _build_env()
 print(f"[session] launching Chrome on :0 (real desktop)...")

 _proc = subprocess.Popen(
 ["google-chrome"] + CHROME_FLAGS + ["about:blank"],
 env=env,
 stdout=subprocess.DEVNULL,
 stderr=subprocess.DEVNULL,
 start_new_session=True,
 )

 time.sleep(3)

 if _proc.poll() is not None:
 raise RuntimeError(
 "Chrome exited on :0\n"
 "Make sure x11vnc is running: bash start_vnc.sh\n"
 "Check XAUTHORITY is correct"
 )

 _port_is_ready(CDP_PORT)
 print(f"[session] ✅ Chrome on :0 (PID {_proc.pid})")
 print(f"[session] → Chrome window visible on your desktop")

 try:
 requests.get(
 f"http://localhost:{CDP_PORT}/json/new?http://example.com",
 timeout=5
 )
 time.sleep(2)
 except Exception:
 pass

 _ctrl = CDPTyper()
 _ctrl._chrome = _proc
 _ctrl._connect()
 return _ctrl


def reset(url="about:blank", wait=1.5):
 ctrl = get_ctrl()
 try:
 ctrl._send("Page.navigate", {"url": url})
 time.sleep(wait)
 except Exception as e:
 print(f"[session] reset failed: {e}")
 ctrl._connect()
 ctrl._send("Page.navigate", {"url": url})
 time.sleep(wait)


def close():
 global _proc, _ctrl
 if _ctrl:
 try: _ctrl.close()
 except Exception: pass
 if _proc:
 try:
 import signal
 os.killpg(os.getpgid(_proc.pid), signal.SIGTERM)
 _proc.wait(timeout=5)
 except Exception:
 try: _proc.kill()
 except Exception: pass
 subprocess.run(
 ["pkill", "-f", f"remote-debugging-port={CDP_PORT}"],
 capture_output=True
 )
 _proc = None
 _ctrl = None
 print("[session] Chrome closed")
