import urllib.request
import numpy as np

from diablorun_igt import inventory_detection, inventory_calibration
from .utils import get_image_rect, get_jpg_b64_buffer, save_bgr, draw_rect


class InventoryManager:
    def __init__(self, api_url, api_key, calibration=None):
        self.api_url = api_url
        self.api_key = api_key

        self.calibrated = None
        self.calibration = calibration

        self.last_description_bgr = None
        self.last_description_rect = None

        self.last_readable_bgr = None
        self.send_images_when_readable = set()

        self.prev_bgr = None
        self.prev_inventory_open = False
        self.prev_empty_slots = set()
        self.prev_hover_state = None
    
    def check_calibration(self, bgr):
        try:
            self.calibrated = bgr.shape == self.calibration["shape"]
        except KeyError:
            self.calibrated = False

        return self.calibrated
    
    def get_emptied_item_slots(self, bgr):
        empty_slots = inventory_detection.get_empty_item_slots(
            self.calibration, bgr)
        emptied_item_slots = empty_slots - self.prev_empty_slots

        if len(emptied_item_slots) > 0:
            self.post_remove_items(emptied_item_slots)

        self.prev_empty_slots = empty_slots

        return emptied_item_slots
    
    def handle_frame(self, bgr, cursor, cursor_visible):
        # Check calibration
        if not self.check_calibration(bgr):
            return
        
        # Check for emptied item slots if inventory is open
        is_inventory_open = inventory_detection.is_inventory_open(self.calibration, bgr)

        if is_inventory_open:
            self.get_emptied_item_slots(bgr)

        # Check if cursor is on an item slot if the inventory was open on previous frame
        if cursor and cursor_visible and self.prev_inventory_open:
            item_slot_hover = inventory_detection.get_hovered_item_slot(self.calibration, bgr, cursor)

            if item_slot_hover:
                description_rect = inventory_detection.get_item_description_rect(bgr, cursor)
                hover_state = item_slot_hover[0], description_rect is None
            else:
                description_rect = None
                hover_state = None

            if hover_state != self.prev_hover_state and item_slot_hover and not item_slot_hover[0] in self.prev_empty_slots and description_rect:
                self.post_item(
                    item_slot_hover[0],
                    get_image_rect(self.prev_bgr, item_slot_hover[1]),
                    get_image_rect(bgr, description_rect))
        else:
            hover_state = None

        self.prev_hover_state = hover_state
        self.prev_bgr = bgr
        self.prev_inventory_open = is_inventory_open

    def handle_frame_smarter(self, bgr, cursor, cursor_visible):
        # Check calibration
        if not self.check_calibration(bgr):
            return

        # Check if there is an item description box on the screen
        description_rect = inventory_detection.get_item_description_rect(
            bgr, cursor)

        if description_rect:
            self.last_description_bgr = bgr
            self.last_description_rect = description_rect

        # Check if item images are readable from current frame
        item_images_readable = cursor_visible and description_rect is None and \
            inventory_detection.is_inventory_open(self.calibration, bgr)

        if item_images_readable:
            self.last_readable_bgr = bgr

            # Check for emptied item slots
            emptied_item_slots = self.get_emptied_item_slots(bgr)

            # Re-send item images that are out of sync with description
            if len(self.send_images_when_readable) > 0:
                rects = inventory_detection.get_item_slot_rects(
                    self.calibration, bgr)
                sent_slots = set()

                for slot in self.send_images_when_readable:
                    if not slot in emptied_item_slots and slot[1] in rects:
                        self.post_item(slot, get_image_rect(
                            bgr, rects[slot[1]]), None)
                        sent_slots.add(slot)

                for slot in sent_slots:
                    self.send_images_when_readable.remove(slot)

        # Check if an item slot is currently hovered
        item_slot_hover = inventory_detection.get_hovered_item_slot(self.calibration, bgr, cursor)
        item_slot_highlighted = item_slot_hover and inventory_detection.is_item_rect_highlighted(
            bgr, item_slot_hover[2])

        # Check for changes in hover state
        hover_state = item_slot_hover and item_slot_hover[0], \
            description_rect is None, item_slot_highlighted

        if hover_state == self.prev_hover_state:
            return

        self.prev_hover_state = hover_state

        # Handle item slot hover
        if item_slot_hover:
            # 1. Description is shown while hovering item slot - easy
            if description_rect:
                if self.last_readable_bgr is None:
                    self.send_images_when_readable.add(item_slot_hover[0])
                    self.post_item(
                        item_slot_hover[0], None,
                        get_image_rect(bgr, description_rect))
                else:
                    self.post_item(
                        item_slot_hover[0],
                        get_image_rect(self.last_readable_bgr,
                                       item_slot_hover[1]),
                        get_image_rect(bgr, description_rect))

            # 2. Item slot is hovered and highlighted, no description shown - an item is being placed here.
            elif not cursor_visible and item_slot_highlighted and self.last_description_rect:
                # Only the description from a previous frame can be sent right away, item image must be sent later
                self.send_images_when_readable.add(item_slot_hover[0])
                self.post_item(item_slot_hover[0], None, get_image_rect(
                    self.last_description_bgr, self.last_description_rect))

    def post_item(self, slot, item_bgr, description_bgr):
        try:
            data = bytes('{ "container": "' + slot[0] + '", "slot": "' +
                         slot[1] + '", "item_jpg": "', "ascii")
            if item_bgr is not None:
                data += get_jpg_b64_buffer(item_bgr, 480)
            data += bytes('", "description_jpg": "', "ascii")
            if description_bgr is not None:
                data += get_jpg_b64_buffer(description_bgr, 480)
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
        self.calibration = inventory_calibration.get_inventory_rects(bgr)

        bgr_copy = np.copy(bgr)

        for key in ("inventory_rect", "inventory_text_rect", "swap_primary_rect", "swap_secondary_rect"):
            draw_rect(bgr_copy, self.calibration[key])

        for slot in self.calibration["item_slot_rects"]:
            draw_rect(
                bgr_copy, self.calibration["item_slot_rects"][slot])

        for slot in self.calibration["empty_item_slot_rects"]:
            draw_rect(
                bgr_copy, self.calibration["empty_item_slot_rects"][slot])

        save_bgr(bgr_copy, "inventory_calibration.jpg")

        return True
