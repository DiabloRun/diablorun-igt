import win32gui
import win32ui
from ctypes import windll, WinDLL, wintypes, byref, sizeof
from PIL import Image
import time

windll.user32.SetProcessDPIAware()
dwmapi = WinDLL("dwmapi")

hwnd = win32gui.FindWindow(None, 'Diablo II: Resurrected')
start = time.time()
saveDC = None

for i in range(10):
    # Change the line below depending on whether you want the whole window
    # or just the client area.
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bot - top

    print(left, top, right, bot)

    # Get screenshot
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    print(w, h, bmpinfo)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

print(10/(time.time() - start))

if result == 1:
    # PrintWindow Succeeded
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    im.save("test.png")


# 1366x768
# main hand 910, 160, 975, 292
# off hand 1180, 160, 1245, 292
# head 1042, 140, 1110, 206
# body 1042, 227, 1110, 328
# feet 1180, 315, 1245, 380
# hands 910, 315, 975, 380
# left ring 992, 345
# right ring 1126, 345, 1160, 380
# amulet 1126, 200, 1160, 232
# belt 1042, 345, 1110, 380
# gold icon 1025, 554
