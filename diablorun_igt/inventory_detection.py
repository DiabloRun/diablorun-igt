import numpy as np

from diablorun_igt.utils import bgr_to_gray

# BGR
ITEM_SLOT_COLOR = np.array((1, 1, 1))
ITEM_HOVER_COLOR = np.array((10, 30, 6))
ITEM_DESCRIPTION_MAX_GRAY = 12
ITEM_DESCRIPTION_PADDING = 3

ITEM_SLOT_RECT_1920_1080 = {
    'helm': [1527, 108, 1640, 221],
    'primary_left': [1310, 140, 1423, 362],
    'primary_right': [1746, 140, 1859, 362],
    'body_armor': [1527, 249, 1640, 419],
    'gloves': [1309, 391, 1422, 504],
    'belt': [1527, 447, 1640, 503],
    'boots': [1745, 391, 1858, 504],
    'amulet': [1663, 206, 1719, 262],
    'ring_left': [1447, 447, 1503, 503],
    'ring_right': [1663, 447, 1719, 503],
}

ITEM_SLOT_RECT_1366_768 = {
    'helm': [1086, 77, 1166, 157],
    'primary_left': [932, 99, 1012, 257],
    'primary_right': [1242, 99, 1322, 220],
    'body_armor': [1086, 177, 1166, 298],
    'gloves': [932, 278, 1012, 358],
    'belt': [1087, 318, 1167, 358],
    'boots': [1242, 278, 1322, 358],
    'amulet': [1184, 146, 1224, 186],
    'ring_left': [1029, 318, 1069, 358],
    'ring_right': [1184, 318, 1224, 358],
}


def get_item_slot_rects(bgr):
    if bgr.shape[0] == 1080:
        return ITEM_SLOT_RECT_1920_1080
    elif bgr.shape[0] == 768:
        return ITEM_SLOT_RECT_1366_768


def get_item_slot_hover(bgr, rects):
    if rects is None:
        return None
    #n = 0

    for slot in rects:
        l, t, r, b = rects[slot]

        slot_corner_colors = np.array((
            bgr[t+1, l+1],
            bgr[t+1, r-1],
            bgr[b-1, l+1],
            bgr[b-1, r-1]
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

    # the edges are the first and last instances of padding that were found
    return mask.argmax(), bgr.shape[axis] - np.flip(mask).argmax()


def get_item_description_rect(bgr, item_rect):
    item_left, _item_top, item_right, _item_bottom = item_rect

    top, bottom = get_item_description_edges(bgr[:, item_left:item_right], 0)

    if top == 0 or bottom == bgr.shape[0] - 1:
        return None

    left, right = get_item_description_edges(bgr[top:bottom, :], 1)

    return left, top, right, bottom
