import base64
import urllib.request
import numpy as np

from diablorun_igt import inventory_detection, inventory_calibration
from .utils import get_image_rect, get_jpg, save_rgb, draw_rect


class InventoryManager:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

        self.last_description_bgr = None
        self.last_description_rect = None

        self.last_readable_bgr = None
        self.send_images_when_readable = set()

        self.prev_empty_slots = set()
        self.prev_hover_state = None
        #self.no_description_rect_frames = 0

    def handle_frame(self, bgr, cursor, cursor_visible):
        # Check if there is an item description box on the screen
        description_rect = inventory_detection.get_item_description_rect(
            bgr, cursor)

        if description_rect:
            self.last_description_bgr = bgr
            self.last_description_rect = description_rect
        #    self.no_description_rect_frames = 0
        # else:
        #    self.no_description_rect_frames += 1

        # Check if item images are readable from current frame
        item_images_readable = cursor_visible and description_rect is None and inventory_detection.is_inventory_open(
            bgr)

        if item_images_readable:
            self.last_readable_bgr = bgr

            # Check for emptied item slots
            empty_slots = inventory_detection.get_empty_item_slots(bgr)
            emptied_item_slots = empty_slots - self.prev_empty_slots

            if len(emptied_item_slots) > 0:
                self.post_remove_items(emptied_item_slots)

            self.prev_empty_slots = empty_slots

            # Re-send item images that are out of sync with description
            if len(self.send_images_when_readable) > 0:
                rects = inventory_detection.get_item_slot_rects(bgr)
                sent_slots = set()

                for slot in self.send_images_when_readable:
                    if not slot in emptied_item_slots and slot[1] in rects:
                        self.post_item(slot, get_image_rect(
                            bgr, rects[slot[1]]), None)
                        sent_slots.add(slot)

                for slot in sent_slots:
                    self.send_images_when_readable.remove(slot)

        # Check if an item slot is currently hovered
        item_slot_hover = inventory_detection.get_hovered_item_slot(
            bgr, cursor)
        item_slot_highlighted = item_slot_hover and inventory_detection.is_item_rect_highlighted(
            bgr, item_slot_hover[2])

        # Check for changes in hover state
        hover_state = item_slot_hover and item_slot_hover[:2], \
            description_rect is None, item_slot_highlighted

        if hover_state == self.prev_hover_state:
            return

        self.prev_hover_state = hover_state

        # Handle item slot hover
        if item_slot_hover:
            # 1. Description is shown while hovering item slot - easy
            if description_rect:
                if self.last_readable_bgr is None:
                    self.send_images_when_readable.add(item_slot_hover[:2])
                    self.post_item(
                        item_slot_hover[:2], None,
                        get_image_rect(bgr, description_rect))
                else:
                    self.post_item(
                        item_slot_hover[:2],
                        get_image_rect(self.last_readable_bgr,
                                       item_slot_hover[2]),
                        get_image_rect(bgr, description_rect))

            # 2. Item slot is hovered and highlighted, no description shown - an item is being placed here.
            elif not cursor_visible and item_slot_highlighted and self.last_description_rect:
                # Only the description from a previous frame can be sent right away, item image must be sent later
                self.send_images_when_readable.add(item_slot_hover[:2])
                self.post_item(item_slot_hover[:2], None, get_image_rect(
                    self.last_description_bgr, self.last_description_rect))

    def post_item(self, slot, item_bgr, description_bgr):
        try:
            data = bytes('{ "container": "' + slot[0] + '", "slot": "' +
                         slot[1] + '", "item_jpg": "', "ascii")
            if item_bgr is not None:
                data += base64.b64encode(get_jpg(item_bgr).getbuffer())
            data += bytes('", "description_jpg": "', "ascii")
            if description_bgr is not None:
                data += base64.b64encode(get_jpg(description_bgr).getbuffer())
            data += bytes('" }', "ascii")

            req = urllib.request.Request(self.api_url + "/d2r/item", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + self.api_key)
            res = urllib.request.urlopen(req)

            print("post_item", slot, res.read())
        except Exception as error:
            print(error)
            pass

    def post_remove_items(self, emptied_item_slots):
        try:
            data = bytes('[', "ascii")

            for i, (container, slot) in enumerate(emptied_item_slots):
                if i > 0:
                    data += bytes(",", "ascii")
                data += bytes('["' + container + '", "' + slot + '"]', "ascii")
            data += bytes(']', "ascii")

            req = urllib.request.Request(
                self.api_url + "/d2r/remove-items", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + self.api_key)
            res = urllib.request.urlopen(req)

            print("post_remove_items", res.read())
        except Exception as error:
            print(error)
            pass

    def calibrate(self, bgr):
        rects = inventory_calibration.get_inventory_rects(bgr)
        bgr_copy = np.copy(bgr)

        for name in rects:
            draw_rect(bgr_copy, rects[name])

        save_rgb(bgr_copy, "inventory_calibration.jpg")

        return rects
