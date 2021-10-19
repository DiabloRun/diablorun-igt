import numpy as np
from PIL import Image

# BGR
ITEM_SLOT_COLOR = np.array((1, 1, 1))
ITEM_HOVER_COLOR = np.array((10, 30, 6))

ITEM_SLOT_COORDINATES_1080 = {
    'helm': [1527, 108, 113, 113],
    'primary_left': [1310, 140, 113, 222],
    'primary_right': [1746, 140, 113, 222],
    'body_armor': [1527, 249, 113, 170],
    'gloves': [1309, 391, 113, 113],
    'belt': [1527, 447, 113, 56],
    'boots': [1745, 391, 113, 113],
    'amulet': [1663, 206, 56, 56],
    'ring_left': [1447, 447, 56, 56],
    'ring_right': [1663, 447, 56, 56]
}

ITEM_SLOT_COORDINATES_768 = {
    'helm': (1086, 77, 80, 80),
    'primary_left': (932, 99, 80, 158),
    'primary_right': (1242, 99, 80, 158),
    'body_armor': (1086, 177, 80, 121),
    'gloves': (932, 278, 80, 80),
    'belt': (1087, 318, 80, 40),
    'boots': (1242, 278, 80, 80),
    'amulet': (1184, 146, 40, 40),
    'ring_left': (1029, 318, 40, 40),
    'ring_right': (1184, 318, 40, 40)
}


def get_item_slot_hover(rgb):
    if rgb.shape[0] == 1080:
        coordinates = ITEM_SLOT_COORDINATES_1080
    elif rgb.shape[0] == 768:
        coordinates = ITEM_SLOT_COORDINATES_768
    else:
        return None

    #n = 0

    for slot in coordinates:
        x, y, w, h = coordinates[slot]

        slot_corner_colors = np.array((
            rgb[y+1, x+1],
            rgb[y+1, x+w-2],
            rgb[y+h-2, x+w-2],
            rgb[y+h-2, x+w-2]
        ))

        #slot_image = rgb[y:y+h, x:x+w]
        #Image.fromarray(slot_image).save("debug/" + slot + ".png")

        # if np.sum(np.all(np.abs(slot_corner_colors - ITEM_SLOT_COLOR) < 10, axis=1)) > 1:
        #    n += 1

        if np.sum(np.all(np.abs(slot_corner_colors - ITEM_HOVER_COLOR) < 10, axis=1)) > 1:
            return slot
            #print("hover", slot, slot_corner_colors)

    # print(n)
