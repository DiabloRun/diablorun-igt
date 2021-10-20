import os
import numpy as np
from PIL import Image
import glob
import time

from diablorun_igt.inventory_detection import get_item_description_edges, get_item_description_rect, get_item_slot_coordinates, get_item_slot_hover


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def save_rgb(bgr, path):
    rgb = Image.fromarray(bgr[:, :, ::-1].astype('uint8'), 'RGB')
    rgb.save(path)
    print("saved", path)


def save_grayscale(values, path):
    rgb = Image.fromarray(values.astype('uint8'), 'L')
    rgb.save(path)
    print("saved", path)


if __name__ == "__main__":
    os.makedirs("debug", exist_ok=True)

    for image_path in glob.glob("test_images/inventory/**.png"):
        image_name = os.path.basename(image_path)
        bgr = get_bgr(image_path)

        coordinates = get_item_slot_coordinates(bgr)
        slot = get_item_slot_hover(bgr, coordinates)

        if slot != None:
            left, top, right, bottom = get_item_description_rect(
                bgr, coordinates[slot])
            save_rgb(bgr[top:bottom, left:right], image_name + "_inv.png")
