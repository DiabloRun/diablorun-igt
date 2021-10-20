import time
import os
from PIL import Image
from queue import Queue

from diablorun_igt.inventory_detection import get_item_description_rect, get_item_slot_hover, get_item_slot_rects
from diablorun_igt.utils import bgr_to_rgb

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
        self.previous_item_slot_hover = None

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

            # Check loading
            is_loading = loading_detection.is_loading(bgr)

            if is_loading != self.state["is_loading"]:
                self.state["is_loading"] = is_loading
                self.changes.put_nowait(
                    {"event": "is_loading_change", "value": is_loading})

                if is_loading and self.is_loading_output:
                    self.save_rgb(bgr, os.path.join(self.is_loading_output,
                                                    str(time.time()) + ".jpg"))

            if is_loading:
                self.status = "loading"
                continue

            # Check item hover
            item_slot_rects = get_item_slot_rects(bgr)
            item_slot_hover = get_item_slot_hover(bgr, item_slot_rects)

            if item_slot_hover and item_slot_hover != self.previous_item_slot_hover:
                item_rect = item_slot_rects[item_slot_hover]
                item_description_rect = get_item_description_rect(
                    bgr, item_rect)

                if item_description_rect != None:
                    self.save_rgb_rect(
                        bgr, item_rect, "debug/" + item_slot_hover + ".jpg")
                    self.save_rgb_rect(
                        bgr, item_description_rect, "debug/" + item_slot_hover + "_description.jpg")
                else:
                    item_slot_hover = None

            self.previous_item_slot_hover = item_slot_hover

            if item_slot_hover:
                self.status = "hover " + item_slot_hover
                continue

            # Nothing of interest detected
            self.status = "playing"

    def save_rgb(self, bgr, path):
        rgb = bgr_to_rgb(bgr)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Image.fromarray(rgb.astype('uint8'), 'RGB').save(path)

        print("saved", path)

    def save_rgb_rect(self, bgr, rect, path):
        l, t, r, b = rect
        self.save_rgb(bgr[t:b, l:r], path)

    def stop(self):
        self.running = False
