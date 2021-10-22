import numpy as np
from PIL import Image
import glob

from diablorun_igt import inventory_detection


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


if __name__ == "__main__":
    primary_images = [
        "test_images/inventory/hover_helm.png",
        "test_images/inventory/inv1-1366x768.png",
        "test_images/inventory/inv2-1366x768.png",
        "test_images/inventory/inv10.png",
        "test_images/inventory/necro1.png",
        "test_images/inventory/test.png"
    ]

    secondary_images = [
        "test_images/empty_inventory/empty.png",
        "test_images/inventory/hover_secondary_left.png",
        "test_images/inventory/inv9.png"
    ]

    for image_path in primary_images:
        image_rgb = get_bgr(image_path)
        item_slot_rects = inventory_detection.get_item_slot_rects(image_rgb)
        print("primary", "primary_left" in item_slot_rects)

    for image_path in secondary_images:
        image_rgb = get_bgr(image_path)
        item_slot_rects = inventory_detection.get_item_slot_rects(image_rgb)
        print("secondary", "secondary_left" in item_slot_rects)
