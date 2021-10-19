import time
import os
from PIL import Image
from queue import Queue

from diablorun_igt.inventory_detection import get_item_slot_hover

from .window_capture import WindowCapture, WindowCaptureFailed, WindowNotFound
from . import loading_detection


class DiabloRunClient:
    def __init__(self, is_loading_output=None):
        self.running = False
        self.changes = Queue()
        self.state = {
            "is_loading": False
        }

        self.status = "not found"
        self.is_loading_output = is_loading_output

    def run(self):
        self.running = True
        window_capture = WindowCapture()

        while self.running:
            time.sleep(0.01)

            try:
                bgr = window_capture.get_bgr()
            except WindowNotFound:
                self.status = "not found"
                continue
            except WindowCaptureFailed:
                self.status = "minimized"
                continue

            is_loading = loading_detection.is_loading(bgr)

            if is_loading != self.state["is_loading"]:
                self.state["is_loading"] = is_loading
                self.changes.put_nowait(
                    {"event": "is_loading_change", "value": is_loading})

                if is_loading and self.is_loading_output:
                    rgb = Image.fromarray(
                        bgr[:, :, ::-1].astype('uint8'), 'RGB')
                    rgb.save(os.path.join(self.is_loading_output,
                                          str(time.time()) + ".jpg"))

            if is_loading:
                self.status = "loading"
                continue

            item_slot_hover = get_item_slot_hover(bgr)

            if item_slot_hover:
                self.status = "hover " + item_slot_hover
                continue

            self.status = "Playing"

    def stop(self):
        self.running = False
