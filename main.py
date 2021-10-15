import mss
import mss.tools
import win32gui
import numpy as np
import time
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 16834))

horizontal_margin = 50
black_color_threshold = 10
black_min_length = 50

hwnd = win32gui.FindWindow(None, 'Diablo II: Resurrected')
loading = False

with mss.mss() as sct:
    while True:
        try:
            hwnd_rect = win32gui.GetWindowRect(hwnd)
            vertical_middle = (hwnd_rect[1] + hwnd_rect[3]) // 2
            rect_inner = (hwnd_rect[0] + horizontal_margin, vertical_middle, hwnd_rect[2] - horizontal_margin, vertical_middle + 1)
            screenshot = sct.grab(rect_inner)
            #mss.tools.to_png(screenshot.rgb, screenshot.size, output="grab.png")

            img = np.array(screenshot)[...,:3]
            img_mean = img.mean(axis=2).flatten()

            black_mask = img_mean > black_color_threshold
            left_border = black_mask.argmax()
            right_border = np.flip(black_mask).argmax()

            loading_now = left_border >= black_min_length and right_border >= black_min_length and 1 - left_border/right_border < 0.05

            if loading != loading_now:
                if loading_now:
                    s.send(b"pausegametime\r\n")
                else:
                    s.send(b"unpausegametime\r\n")
                
                loading = loading_now

            time.sleep(0.01)
        except KeyboardInterrupt:
            break
