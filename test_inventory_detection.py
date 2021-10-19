import os
import numpy as np
from PIL import Image
import glob


def get_rgb(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3]


INVENTORY_SLOT_COLOR = np.array((1, 1, 1))

if __name__ == "__main__":
    slots = {}
    corner_coords = []

    with open("inventory.csv") as f:
        header = True

        for line in f:
            if header:
                header = False
                continue

            res_width, res_height, slot, x, y, w, h = line.strip().split(",")
            slots[slot] = [int(x), int(y), int(w), int(h)]

    hover_color = np.array((8, 28, 4))

    for image_path in glob.glob("test_images/*/**.png"):
        image_name = os.path.basename(image_path)
        image_rgb = get_rgb(image_path)

        if image_rgb.shape[0] != 1080 or image_rgb.shape[1] != 1920:
            continue

        yes = []

        for slot in slots:
            x, y, w, h = slots[slot]
            slot_corner_colors = np.array((
                image_rgb[y+1, x+1],
                image_rgb[y+1, x+w-2],
                image_rgb[y+h-2, x+w-2],
                image_rgb[y+h-2, x+w-2]
            ))

            if np.sum(np.all(np.abs(slot_corner_colors - INVENTORY_SLOT_COLOR) < 10, axis=1)) > 1:
                yes.append(slot)

        # print(np.sum(np.sum(np.array(corner_colors) ** 2, 1) < 10))
        print(image_path, len(yes))

        corner_colors = image_rgb[corner_coords]
