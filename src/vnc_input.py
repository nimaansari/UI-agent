#!/usr/bin/env python3
"""
vnc_input.py
Send mouse/keyboard input via VNC RFB protocol.
Works on :0 where xdotool is blocked by VirtualBox.
"""

import socket, struct, time

VNC_HOST = "localhost"
VNC_PORT = 5900

# X11 Keysym constants
KEY_RETURN = 0xff0d
KEY_TAB = 0xff09
KEY_ESCAPE = 0xff1b
KEY_BACKSPACE = 0xff08
KEY_DELETE = 0xffff
KEY_HOME = 0xff50
KEY_END = 0xff57
KEY_CTRL_L = 0xffe3
KEY_SHIFT_L = 0xffe1
KEY_ALT_L = 0xffe9
KEY_F4 = 0xffc1
KEY_F5 = 0xffc2


class VNCInput:
    def __init__(self, host=VNC_HOST, port=VNC_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self._connect()

    def _connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # RFB 3.3 handshake
        self.sock.recv(12)  # server version
        self.sock.send(b"RFB 003.003\n")  # client version
        sec = struct.unpack(">I", self.sock.recv(4))[0]  # security type

        if sec == 2:
            # VNC auth — send blank password response
            self.sock.recv(16)  # challenge
            self.sock.send(b'\x00' * 16)  # response
            self.sock.recv(4)  # auth result

        self.sock.send(b"\x01")  # ClientInit: shared
        si = self.sock.recv(24)  # ServerInit header
        name_len = struct.unpack(">I", si[20:24])[0]
        self.sock.recv(name_len)  # desktop name
        print(f"[vnc] ✅ connected to {self.host}:{self.port}")

    def _ptr(self, x, y, mask=0):
        self.sock.send(struct.pack(">BBHH", 5, mask, x, y))

    def _key(self, keysym, down=True):
        self.sock.send(struct.pack(">BBxxI", 4, 1 if down else 0, keysym))

    def move(self, x, y):
        self._ptr(x, y, 0)

    def click(self, x, y):
        self._ptr(x, y, 0)
        time.sleep(0.05)
        self._ptr(x, y, 1)  # left button down
        time.sleep(0.08)
        self._ptr(x, y, 0)  # release
        print(f"[vnc] click ({x}, {y})")

    def double_click(self, x, y):
        self.click(x, y)
        time.sleep(0.1)
        self.click(x, y)
        print(f"[vnc] double_click ({x}, {y})")

    def right_click(self, x, y):
        self._ptr(x, y, 0)
        time.sleep(0.05)
        self._ptr(x, y, 4)  # right button
        time.sleep(0.08)
        self._ptr(x, y, 0)
        print(f"[vnc] right_click ({x}, {y})")

    def scroll_down(self, x, y, clicks=3):
        for _ in range(clicks):
            self._ptr(x, y, 16)
            time.sleep(0.05)
            self._ptr(x, y, 0)
            time.sleep(0.05)

    def scroll_up(self, x, y, clicks=3):
        for _ in range(clicks):
            self._ptr(x, y, 8)
            time.sleep(0.05)
            self._ptr(x, y, 0)
            time.sleep(0.05)

    def type_text(self, text, delay=0.04):
        for char in text:
            keysym = ord(char)
            self._key(keysym, down=True)
            time.sleep(delay)
            self._key(keysym, down=False)
            time.sleep(delay)
        print(f"[vnc] typed: '{text[:50]}'")

    def key(self, keysym):
        self._key(keysym, down=True)
        time.sleep(0.05)
        self._key(keysym, down=False)

    def ctrl(self, char):
        keysym = ord(char.lower())
        self._key(KEY_CTRL_L, down=True)
        time.sleep(0.02)
        self._key(keysym, down=True)
        time.sleep(0.02)
        self._key(keysym, down=False)
        time.sleep(0.02)
        self._key(KEY_CTRL_L, down=False)
        print(f"[vnc] ctrl+{char}")

    def press_return(self):
        self.key(KEY_RETURN)

    def press_tab(self):
        self.key(KEY_TAB)

    def press_escape(self):
        self.key(KEY_ESCAPE)

    def close(self):
        if self.sock:
            self.sock.close()
