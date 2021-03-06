import sys
import numpy as np

from diablorun_igt.utils import load_bgr


class WindowNotFound(Exception):
    pass


class WindowCaptureFailed(Exception):
    pass


if sys.platform == "win32":
    import win32gui
    import win32ui
    import pywintypes
    from ctypes import windll

    windll.user32.SetProcessDPIAware()

    CAPTUREBLT = 0x40000000
    DIB_RGB_COLORS = 0
    SRCCOPY = 0x00CC0020

    class WindowCapture:
        def __init__(self, name: str = "Diablo II: Resurrected"):
            self.name = name

        def get_snapshot(self) -> np.ndarray:
            hwnd = win32gui.FindWindow(None, self.name)

            # Get window rect
            try:
                rect = win32gui.GetClientRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
            except pywintypes.error:
                raise WindowNotFound()

            if width <= 0 or height <= 0:
                raise WindowCaptureFailed()

            # Create DC
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            bit_map = win32ui.CreateBitmap()
            bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bit_map)

            # Get cursor position
            cursor = win32gui.ScreenToClient(hwnd, win32gui.GetCursorPos())

            if cursor[0] < 0 or cursor[0] >= width or cursor[1] < 0 or cursor[1] >= height:
                cursor = None
            
            # Get screenshot
            result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)

            if result != 1:
                raise WindowCaptureFailed()

            bmpstr = bit_map.GetBitmapBits(True)

            # Release objects
            win32gui.DeleteObject(bit_map.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            # Convert to np array
            return np.frombuffer(bmpstr, dtype=np.uint8).reshape(height, width, 4)[..., :3], cursor, win32gui.GetCursorInfo()[0]

elif sys.platform == "darwin":
    class WindowCapture:
        def get_snapshot(self):
            bgr = load_bgr("test_images/empty_inventory/empty.png")

            return bgr, None, True
