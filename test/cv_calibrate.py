import os
import numpy as np
from PIL import Image
import glob
import cv2

from diablorun_igt.inventory_calibration import get_inventory_rects


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def draw_rect(bgr, rect, color=(0, 0, 255)):
    x0, y0, x1, y1 = rect
    bgr[y0:y1, x0:x0+1] = color
    bgr[y0:y1, x1-1:x1] = color
    bgr[y0:y0+1, x0:x1] = color
    bgr[y1-1:y1, x0:x1] = color

if __name__ == "__main__":
    for image_path in glob.glob("test_images/empty_inventory/empty_shenk.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = get_bgr(image_path)

        calibration = get_inventory_rects(bgr)

        # First detected rects
        for key in ("inventory_rect",):
            draw_rect(bgr, calibration[key], (0, 0, 255))

        # Secondary detected rects
        for slot in calibration["item_slot_rects"]:
            draw_rect(
                bgr, calibration["item_slot_rects"][slot], (0, 255, 255))

        # Tertiary detected rects
        for key in ("inventory_text_rect", "swap_primary_rect", "swap_secondary_rect"):
            draw_rect(bgr, calibration[key], (255, 0, 255))

        for slot in calibration["empty_item_slot_rects"]:
            draw_rect(
                bgr, calibration["empty_item_slot_rects"][slot], (255, 255, 0))

        left = calibration["inventory_rect"][0]
        width = calibration["inventory_rect"][2] - left

        cv2.imwrite("docs/inventory_calibration/cv.jpg", bgr[:, int(left - 0.1*width):])
