import time
from queue import Queue

from .window_capture import WindowCapture
from . import loading_detection


class DiabloRunClient:
    def __init__(self):
        self.running = False
        self.changes = Queue()
        self.state = {
            "is_loading": False
        }

        self.capture_failed = False
        self.capture_failed_at = None

    def run(self):
        self.running = True
        window_capture = WindowCapture()

        while self.running:
            time.sleep(0.01)

            if self.capture_failed and time.time() - self.capture_failed_at < 1:
                continue

            try:
                rgb = window_capture.get_rgb()
            except Exception:
                print("Could not capture D2R window, trying again in 1 second...")
                self.capture_failed = True
                self.capture_failed_at = time.time()
                continue

            is_loading = loading_detection.is_loading(rgb)

            if is_loading != self.state["is_loading"]:
                self.state["is_loading"] = is_loading
                self.changes.put_nowait(
                    {"event": "is_loading_change", "value": is_loading})

    def stop(self):
        self.running = False
