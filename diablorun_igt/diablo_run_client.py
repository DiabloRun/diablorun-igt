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
        self.empty_slots = {"character": []}
        self.resend_item_image = None

        self.is_loading = False
        self.hovered_item = None
        self.hovered_item_has_description = False
        self.hovered_item_is_highlighted = False
        self.last_item_description_bgr = None
        self.last_item_description_rect = None

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
        if not self.api_key or self.is_loading:
            return

        if inventory_detection.is_inventory_open(self.bgr):
            self.inventory_bgr = self.bgr

            # Check for empty slots
            empty_slots = inventory_detection.get_empty_item_slots(self.bgr)
            removed_items = []

            for container in empty_slots:
                for slot in empty_slots[container]:
                    if slot not in self.empty_slots[container]:
                        removed_items.append((container, slot))

            if len(removed_items):
                self.post_remove_items(removed_items)

            self.empty_slots = empty_slots

            # Check for item image to resend
            if self.resend_item_image:
                container, slot = self.resend_item_image
                rects = inventory_detection.get_item_slot_rects(self.bgr)
                self.post_item(container, slot, get_jpg(
                    self.bgr, rects[slot]), None)
                self.resend_item_image = None

    def handle_item_hover(self):
        if not self.api_key or self.is_loading or not self.cursor or self.inventory_bgr is None:
            return

        hovered_item = get_hovered_item(self.bgr, self.cursor)
        description_rect = get_item_description_rect(self.bgr, self.cursor)
        hovered_item_has_description = hovered_item and description_rect is not None
        hovered_item_is_highlighted = hovered_item and inventory_detection.is_item_rect_highlighted(
            self.bgr, hovered_item[2])

        if description_rect:
            self.last_item_description_bgr = self.bgr
            self.last_item_description_rect = description_rect

        if hovered_item:
            container, slot, item_rect = hovered_item

            if self.hovered_item and container == self.hovered_item[0] and slot == self.hovered_item[1] and hovered_item_has_description == self.hovered_item_has_description and hovered_item_is_highlighted == self.hovered_item_is_highlighted:
                return

            if description_rect or hovered_item_is_highlighted:
                self.post_item(container, slot, get_jpg(
                    self.inventory_bgr, item_rect), get_jpg(self.last_item_description_bgr, self.last_item_description_rect))

                if not description_rect:
                    self.resend_item_image = (container, slot)

        self.hovered_item = hovered_item
        self.hovered_item_has_description = hovered_item_has_description
        self.hovered_item_is_highlighted = hovered_item_is_highlighted

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
            if item_jpg is not None:
                data += base64.b64encode(item_jpg.getbuffer())
            data += bytes('", "description_jpg": "', "ascii")
            if description_jpg is not None:
                data += base64.b64encode(description_jpg.getbuffer())
            data += bytes('" }', "ascii")

            req = urllib.request.Request(self.api_url + "/d2r/item", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + self.api_key)
            res = urllib.request.urlopen(req)

            print("item", container, slot, res.read())
        except Exception as error:
            print(error)
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

            print("remove_items", res.read())
        except Exception as error:
            print(error)
            pass
