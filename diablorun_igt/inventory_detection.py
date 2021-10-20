import numpy as np

from diablorun_igt.utils import bgr_to_gray

# BGR
ITEM_SLOT_COLOR = np.array((1, 1, 1))
ITEM_HOVER_COLOR = np.array((10, 30, 6))
ITEM_DESCRIPTION_MAX_GRAY = 12
ITEM_DESCRIPTION_PADDING = 5

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


def get_item_slot_coordinates(bgr):
    if bgr.shape[0] == 1080:
        return ITEM_SLOT_COORDINATES_1080
    elif bgr.shape[0] == 768:
        return ITEM_SLOT_COORDINATES_768


def get_item_slot_hover(bgr, coordinates):
    if coordinates is None:
        return None
    #n = 0

    for slot in coordinates:
        x, y, w, h = coordinates[slot]

        slot_corner_colors = np.array((
            bgr[y+1, x+1],
            bgr[y+1, x+w-2],
            bgr[y+h-2, x+w-2],
            bgr[y+h-2, x+w-2]
        ))

        #slot_image = rgb[y:y+h, x:x+w]
        #Image.fromarray(slot_image).save("debug/" + slot + ".png")

        # if np.sum(np.all(np.abs(slot_corner_colors - ITEM_SLOT_COLOR) < 10, axis=1)) > 1:
        #    n += 1

        if np.sum(np.all(np.abs(slot_corner_colors - ITEM_HOVER_COLOR) < 10, axis=1)) > 1:
            return slot
            #print("hover", slot, slot_corner_colors)

    # print(n)


def get_item_description_edges(bgr, axis):
    # Get item description dark background mask
    mask = bgr_to_gray(bgr) <= ITEM_DESCRIPTION_MAX_GRAY

    # Find horizontal lines where background is fully detected
    opposite_axis = 1 - axis
    mask = mask.sum(axis=opposite_axis) == mask.shape[opposite_axis]

    # Find padding-sized blocks of adjacent horizontal lines
    mask = np.convolve(mask, np.ones(ITEM_DESCRIPTION_PADDING), "valid")
    mask = mask == ITEM_DESCRIPTION_PADDING

    # top and bottom are the first and last instances of padding that were found
    return mask.argmax(), bgr.shape[axis] - np.flip(mask).argmax()


def get_item_description_rect(bgr, item_rect):
    x, y, w, h = item_rect

    top, bottom = get_item_description_edges(bgr[:, x:x+w], 0)
    left, right = get_item_description_edges(bgr[top:bottom, :], 1)

    return left, top, right, bottom
