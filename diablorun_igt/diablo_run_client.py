import time
import os
from PIL import Image
from queue import Queue

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
        self.capture_failed = False
        self.capture_failed_at = None
        self.is_loading_output = is_loading_output

    def run(self):
        self.running = True
        window_capture = WindowCapture()

        while self.running:
            time.sleep(0.01)

            if self.capture_failed and time.time() - self.capture_failed_at < 1:
                continue

            try:
                rgb = window_capture.get_rgb()
            except WindowNotFound:
                print("D2R window not found, trying again in 1 second...")
                self.status = "not found"
                self.capture_failed = True
                self.capture_failed_at = time.time()
                continue
            except WindowCaptureFailed:
                self.status = "minimized"
                continue

            is_loading = loading_detection.is_loading(rgb)

            if is_loading != self.state["is_loading"]:
                self.state["is_loading"] = is_loading
                self.changes.put_nowait(
                    {"event": "is_loading_change", "value": is_loading})

                if is_loading and self.is_loading_output:
                    im = Image.fromarray(
                        rgb[:, :, ::-1].astype('uint8'), 'RGB')
                    im.save(os.path.join(self.is_loading_output,
                            str(time.time()) + ".jpg"))

            self.status = is_loading and "loading" or "playing"

    def stop(self):
        self.running = False
