import time
import urllib
from queue import Queue
import base64
import urllib.request
from diablorun_igt import inventory_detection

from diablorun_igt.inventory_detection import get_hovered_item, get_item_description_rect
from diablorun_igt.utils import get_jpg, resize_image

from .window_capture import WindowCapture, WindowCaptureFailed, WindowNotFound
from . import loading_detection


class DiabloRunClient:
    def __init__(self, api_url="https://api.diablo.run", api_key=None):
        self.running = False
        self.changes = Queue()

        self.cursor = None
        self.bgr = None
        self.inventory_bgr = None
        self.is_loading = False
        self.hovered_item = None
        self.empty_slots = {"character": []}

        self.status = "not found"
        self.api_url = api_url
        self.api_key = api_key

        self.frames_counted_from = None
        self.frames = 0
        self.fps = 0

    def handle_is_loading(self):
        is_loading = loading_detection.is_loading(self.bgr)

        if is_loading != self.is_loading:
            self.is_loading = is_loading
            self.changes.put_nowait(
                {"event": "is_loading_change", "value": is_loading})

            # if is_loading and self.is_loading_output:
            #    self.save_rgb(bgr, os.path.join(self.is_loading_output,
            #                                    str(time.time()) + ".jpg"))

        if is_loading:
            self.status = "loading"

    def handle_inventory(self):
        if inventory_detection.is_inventory_open(self.bgr):
            self.inventory_bgr = self.bgr

            empty_slots = inventory_detection.get_empty_item_slots(self.bgr)
            removed_items = []

            for container in empty_slots:
                for slot in empty_slots[container]:
                    if slot not in self.empty_slots[container]:
                        removed_items.append((container, slot))

            if len(removed_items):
                self.post_remove_items(removed_items)

            self.empty_slots = empty_slots

    def handle_item_hover(self):
        if self.is_loading or not self.cursor or self.inventory_bgr is None:
            return

        hovered_item = get_hovered_item(self.bgr, self.cursor)

        if hovered_item:
            container, slot, item_rect = hovered_item
            self.status = slot

            if self.hovered_item and container == self.hovered_item[0] and slot == self.hovered_item[1]:
                return

            description_rect = get_item_description_rect(self.bgr, self.cursor)

            if description_rect is None:
                hovered_item = None
            else:
                # save_rgb(self.prev_bgr, "debug/" + slot + ".jpg", item_rect)
                # save_rgb(self.bgr, "debug/" + slot +
                #         "_description.jpg", description_rect)

                if self.api_key:
                    self.post_item(container, slot, get_jpg(
                        self.inventory_bgr, item_rect), get_jpg(self.bgr, description_rect))

        self.hovered_item = hovered_item

    def run(self):
        self.running = True
        self.frames_counted_from = time.time()
        self.frames = 0

        window_capture = WindowCapture()

        while self.running:
            time.sleep(0.01)

            try:
                self.cursor, self.bgr = window_capture.get_snapshot()
                self.status = "playing"
            except WindowNotFound:
                self.status = "not found"
                continue
            except WindowCaptureFailed:
                self.status = "minimized"
                continue

            # Check loading
            self.handle_is_loading()

            # Check inventory
            self.handle_inventory()

            # Check item hover
            self.handle_item_hover()

            # Update FPS
            self.frames += 1

            if self.frames == 30:
                now = time.time()
                self.fps = round(
                    self.frames / (now - self.frames_counted_from))
                self.frames = 0
                self.frames_counted_from = now

    def stop(self):
        self.running = False

    def post_item(self, container, slot, item_jpg, description_jpg):
        try:
            data = bytes('{ "container": "' + container + '", "slot": "' +
                         slot + '", "item_jpg": "', "ascii")
            data += base64.b64encode(item_jpg.getbuffer())
            data += bytes('", "description_jpg": "', "ascii")
            data += base64.b64encode(description_jpg.getbuffer())
            data += bytes('" }', "ascii")

            req = urllib.request.Request(self.api_url + "/d2r/item", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + self.api_key)
            res = urllib.request.urlopen(req)

            print(res.read())
        except Exception as error:
            print(error.message)
            pass

    def post_remove_items(self, removed_items):
        try:
            data = bytes('[', "ascii")

            for i, (container, slot) in enumerate(removed_items):
                if i > 0:
                    data += bytes(",", "ascii")
                data += bytes('["' + container + '", "' + slot + '"]', "ascii")
            data += bytes(']', "ascii")

            req = urllib.request.Request(
                self.api_url + "/d2r/remove-items", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + self.api_key)
            res = urllib.request.urlopen(req)

            print(res.read())
        except Exception as error:
            print(error)
            pass
