import ctypes
import win32gui

class Window:
    def __init__(self):
        self.dwmapi = ctypes.WinDLL("dwmapi")

    def get_hwnd(self):
        return win32gui.FindWindow(None, 'Diablo II: Resurrected')
    
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
