import sys
import mss
import numpy as np

if sys.platform == "win32":
    import win32gui
    import ctypes

    class WindowCapture:
        def __init__(self, name: str = "Diablo II: Resurrected"):
            self.dwmapi = ctypes.WinDLL("dwmapi")
            self.name = name
            self.sct = mss.mss()

        def get_hwnd(self) -> int:
            return win32gui.FindWindow(None, self.name)

        def get_rect(self):
            hwnd = self.get_hwnd()
            rect = ctypes.wintypes.RECT()

            self.dwmapi.DwmGetWindowAttribute(
                ctypes.wintypes.HWND(hwnd),
                ctypes.wintypes.DWORD(9),
                ctypes.byref(rect),
                ctypes.sizeof(rect)
            )

            return (
                rect.left + 1,
                rect.top + 33,
                rect.right - 1,
                rect.bottom - 1
            )

        def get_rgb(self) -> np.ndarray:
            rect = self.get_rect()
            screenshot = self.sct.grab(rect)

            return np.array(screenshot)[..., :3]
