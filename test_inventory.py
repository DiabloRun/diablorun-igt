import numpy as np
from PIL import Image
import glob


def get_rgb(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3]


if __name__ == "__main__":
    slots = {}

    with open("inventory.csv") as f:
        header = True

        for line in f:
            if header:
                header = False
                continue

            res_width, res_height, slot, x, y, w, h = line.strip().split(",")
            slots[slot] = [int(x), int(y), int(w), int(h)]

    hover_color = np.array((8, 28, 4))

    for image_path in glob.glob("test_images/inventory/**.png"):
        image_name = image_path.split("/")[-1]
        image_rgb = get_rgb(image_path)

        for slot in slots:
            x, y, w, h = slots[slot]
            slot_image = image_rgb[y:y+h, x:x+w]

            corners = np.array((
                slot_image[1, 1],
                slot_image[1, -2],
                slot_image[-2, -2],
                slot_image[-2, 1]
            ))

            if (((corners - hover_color) ** 2).sum(axis=1) < 10).sum() > 1:
                print(image_name, slot)

            Image.fromarray(slot_image).save(
                "debug/" + slot + "_" + image_name)
