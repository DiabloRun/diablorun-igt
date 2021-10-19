import os
import numpy as np
from PIL import Image
import glob


def get_rgb(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3]


if __name__ == "__main__":
    os.makedirs("debug", exist_ok=True)

    slots = {}

    with open("inventory.csv") as f:
        header = True

        for line in f:
            if header:
                header = False
                continue

            res_width, res_height, slot, x, y, w, h = line.strip().split(",")
            if res_width != "1366":
                continue
            slots[slot] = [int(x), int(y), int(w), int(h)]

    print(slots)

    hover_color = np.array((8, 28, 4))

    for image_path in glob.glob("test_images/inventory/**.png"):
        image_name = os.path.basename(image_path)
        image_rgb = get_rgb(image_path)

        if image_rgb.shape[0] != 768:
            continue

        corner_colors = []

        for slot in slots:
            x, y, w, h = slots[slot]
            slot_image = image_rgb[y:y+h, x:x+w]
            slot_corner_colors = (
                slot_image[1, 1],
                slot_image[1, -2],
                slot_image[-2, -2],
                slot_image[-2, 1]
            )

            corner_colors += slot_corner_colors

            if (((np.array(slot_corner_colors) - hover_color) ** 2).sum(axis=1) < 10).sum() > 1:
                print(image_name, slot)

            Image.fromarray(slot_image).save(
                "debug/" + slot + "_" + image_name)

        print(np.sum(np.sum(np.array(corner_colors) ** 2, 1) < 10))
