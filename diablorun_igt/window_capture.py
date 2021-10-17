import sys
import numpy as np

if sys.platform == "win32":
    import mss.windows
    mss.windows.CAPTUREBLT = 0

    import mss
    import mss.tools
    import win32gui
    import ctypes

    class WindowCapture:
        def __init__(self, name: str = "Diablo II: Resurrected"):
            self.dwmapi = ctypes.WinDLL("dwmapi")
            self.name = name
            self.sct = mss.mss()
            self.screenshot = None

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
            self.screenshot = self.sct.grab(rect)

            return np.array(self.screenshot)[..., :3]

        def write_last_capture(self, path):
            if self.screenshot:
                mss.tools.to_png(
                    self.screenshot.rgb, self.screenshot.size, output=path)
