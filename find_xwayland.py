#!/usr/bin/env python3
# find_xwayland.py — finds Xwayland display and auth token

import os
import subprocess
import glob

def find_xwayland():
    """
    Find Xwayland display number and auth token.
    Returns (display, auth_file) or (None, None).
    """
    uid = os.getuid()
    run_user = f"/run/user/{uid}"
    results = []

    # Method 1: scan /run/user/UID/ for mutter Xwayland auth
    if os.path.isdir(run_user):
        for f in os.listdir(run_user):
            if "Xwaylandauth" in f or "mutter" in f.lower():
                auth_path = os.path.join(run_user, f)

                # Try to find which display this auth is for
                try:
                    result = subprocess.run(
                        ["xauth", "-f", auth_path, "list"],
                        capture_output=True
                    )
                    output = result.stdout.decode()
                    for line in output.splitlines():
                        if "unix:" in line or "/:" in line:
                            import re
                            match = re.search(r':(\d+)', line)
                            if match:
                                display = f":{match.group(1)}"
                                results.append((display, auth_path))
                                print(f" Found: display={display} auth={os.path.basename(auth_path)}")
                except Exception as e:
                    # Still add it — might work
                    results.append((":0", auth_path))

    # Method 2: Check running Xwayland process
    try:
        result = subprocess.run(
            ["pgrep", "-a", "Xwayland"],
            capture_output=True
        )
        for line in result.stdout.decode().splitlines():
            import re
            match = re.search(r' :(\d+) ', line)
            if match:
                display = f":{match.group(1)}"
                print(f" Xwayland process on {display}")
                for r in results:
                    if r[0] == display:
                        return r
    except:
        pass

    # Method 3: Read gnome-shell environment
    try:
        result = subprocess.run(
            ["pgrep", "-u", str(uid), "gnome-shell"],
            capture_output=True
        )
        pids = result.stdout.decode().strip().splitlines()
        for pid in pids[:1]:  # just first one
            try:
                with open(f"/proc/{pid.strip()}/environ", "rb") as f:
                    env_data = f.read().split(b'\x00')
                    for item in env_data:
                        if b'XAUTHORITY' in item and b'Xwaylandauth' in item:
                            _, v = item.split(b'=', 1)
                            auth_path = v.decode()
                            if os.path.exists(auth_path):
                                results.append((":0", auth_path))
                                print(f" From gnome-shell env: {os.path.basename(auth_path)}")
            except:
                pass
    except:
        pass

    if results:
        return results[0]
    return None, None


if __name__ == "__main__":
    print("Searching for Xwayland display and auth...")
    display, auth = find_xwayland()
    if display and auth:
        print(f"\n✅ Found:")
        print(f" DISPLAY = {display}")
        print(f" XAUTHORITY = {auth}")
        print(f"\nTest connection:")
        print(f" DISPLAY={display} XAUTHORITY={auth} xdpyinfo | head -3")

        env = {**os.environ, "DISPLAY": display, "XAUTHORITY": auth}
        r = subprocess.run(["xdpyinfo"], env=env, capture_output=True)
        if r.returncode == 0:
            print(f"\n✅ Xwayland connection works!")
            print(r.stdout.decode().splitlines()[0])
        else:
            print(f"\n❌ Connection failed: {r.stderr.decode()[:100]}")
    else:
        print("\n❌ Could not find Xwayland display")
        print(" Make sure you are logged in with a Wayland session")
