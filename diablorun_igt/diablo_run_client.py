import time
from queue import Queue
import pickle

from .inventory_manager import InventoryManager
from .window_capture import WindowCapture, WindowCaptureFailed, WindowNotFound
from . import loading_detection


class DiabloRunClient:
    def __init__(self, api_url="https://api.diablo.run", api_key=None):
        self.running = False
        self.changes = Queue()
        self.is_loading = False

        self.status = "not found"
        self.api_url = api_url
        self.api_key = api_key

        self.bgr = None
        self.cursor = None
        self.cursor_visible = False
        self.frames_counted_from = None
        self.frames = 0
        self.fps = 0

        try:
            with open("diablorun.pickle", "rb") as f:
                calibration = pickle.loads(f.read())
        except FileNotFoundError:
            calibration = None

        self.inventory_manager = InventoryManager(
            api_url, api_key, calibration)

    def handle_is_loading(self, bgr):
        is_loading = loading_detection.is_loading(bgr)

        if is_loading != self.is_loading:
            self.is_loading = is_loading
            self.changes.put_nowait(
                {"event": "is_loading_change", "value": is_loading})

            # if is_loading and self.is_loading_output:
            #    self.save_rgb(bgr, os.path.join(self.is_loading_output,
            #                                    str(time.time()) + ".jpg"))

        if is_loading:
            self.status = "loading"

    def run(self):
        self.running = True
        self.frames_counted_from = time.time()
        self.frames = 0

        window_capture = WindowCapture()

        while self.running:
            time.sleep(0.01)

            try:
                self.bgr, self.cursor, self.cursor_visible = window_capture.get_snapshot()
                self.status = "playing"
            except WindowNotFound:
                self.status = "not found"
                continue
            except WindowCaptureFailed:
                self.status = "minimized"
                continue

            # Check loading
            self.handle_is_loading(self.bgr)

            # Check inventory
            if self.api_key and not self.is_loading:
                self.inventory_manager.handle_frame(
                    self.bgr, self.cursor, self.cursor_visible)

            # Update FPS
            self.frames += 1

            if self.frames == 30:
                now = time.time()
                self.fps = round(
                    self.frames / (now - self.frames_counted_from))
                self.frames = 0
                self.frames_counted_from = now
                #print(self.fps)

    def stop(self):
        self.running = False

    def calibrate(self):
        if self.bgr is not None and self.inventory_manager.calibrate(self.bgr):
            with open("diablorun.pickle", "wb") as f:
                f.write(pickle.dumps(self.inventory_manager.calibration))
