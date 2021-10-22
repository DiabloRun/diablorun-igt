import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from diablorun_igt.calibration import get_calibrated_rects

from diablorun_igt.utils import get_image_rect


# BGR
ITEM_DESCRIPTION_BG_COLOR = np.array((2, 2, 2))
ITEM_SLOT_COLOR = np.array((2, 2, 2))
ITEM_HOVER_COLOR = np.array((10, 30, 6))
EMPTY_SLOT_COLOR = np.array((20, 20, 20))

ITEM_SLOT_EMPTY_CENTER = {
    'head': ((26, 26, 25), 2),
    'primary_left': ((13, 13, 13), 2),
    'primary_right': ((13, 13, 13), 2),
    'secondary_left': ((13, 13, 13), 2),
    'secondary_right': ((13, 13, 13), 2),
    'body_armor': ((28, 29, 28), 6),
    'gloves': ((18, 18, 17), 3),
    'belt': ((36, 36, 36), 12),
    'boots': ((25, 24, 23), 4),
    'amulet': ((16, 15, 15), 3),
    'ring_left': ((29, 29, 28), 3),
    'ring_right': ((29, 29, 28), 3)
}


def get_item_slot_rects(bgr):
    rects = get_calibrated_rects(bgr)

    if rects:
        rects = rects.copy()

        swap_primary_brightness = (get_image_rect(bgr, rects['swap_on_primary_left']) +
                                   get_image_rect(bgr, rects['swap_on_primary_right'])).mean()
        swap_secondary_brightness = (get_image_rect(bgr, rects['swap_on_secondary_left']) +
                                     get_image_rect(bgr, rects['swap_on_secondary_right'])).mean()

        if swap_secondary_brightness > swap_primary_brightness:
            del rects["primary_left"]
            del rects["primary_right"]
        else:
            del rects["secondary_left"]
            del rects["secondary_right"]

        del rects["swap_on_primary_left"]
        del rects["swap_on_primary_right"]
        del rects["swap_on_secondary_left"]
        del rects["swap_on_secondary_right"]

    return rects


def get_hovered_item_slot(bgr, cursor):
    if cursor is None:
        return None

    rects = get_item_slot_rects(bgr)

    if rects is None:
        return None

    for slot in rects:
        l, t, r, b = rects[slot]

        if cursor[0] >= l and cursor[0] <= r and cursor[1] >= t and cursor[1] <= b:
            return "character", slot, rects[slot]


def is_item_rect_highlighted(bgr, item_rect):
    l, t, r, b = item_rect

    slot_corner_colors = np.array((
        bgr[t+1, l+1],
        bgr[t+1, r-1],
        bgr[b-1, l+1],
        bgr[b-1, r-1]
    ))

    return np.sum(np.all(np.abs(slot_corner_colors - ITEM_HOVER_COLOR) < 10, axis=1)) > 1


def is_inventory_open(bgr):
    rects = get_item_slot_rects(bgr)

    if rects is None:
        return False

    for slot in rects:
        l, t, r, b = rects[slot]

        slot_corner_colors = np.array((
            bgr[t+1, l+1],
            bgr[t+1, r-1],
            bgr[b-1, l+1],
            bgr[b-1, r-1]
        ))

        if np.sum(np.all(np.abs(slot_corner_colors - ITEM_SLOT_COLOR) < 10, axis=1)) < 2:
            return False

    return True


def get_empty_item_slots(bgr):
    rects = get_item_slot_rects(bgr)

    if rects is None:
        return False

    empty_slots = set()

    for slot in rects:
        l, t, r, b = rects[slot]
        hc, vc = (l + r) // 2, (t + b) // 2
        empty_color, empty_color_range = ITEM_SLOT_EMPTY_CENTER[slot]

        if (np.abs(bgr[vc, hc] - empty_color) <= empty_color_range).all():
            empty_slots.add(("character", slot))

    return empty_slots


def get_item_description_bg_mask(bgr):
    return np.all(np.abs(bgr - ITEM_DESCRIPTION_BG_COLOR) < 8, axis=2)


def get_item_description_rect(bgr, cursor):
    if cursor is None:
        return None

    # 1. Get band around cursor
    band_left, band_right = cursor[0] - 25, cursor[0] + 25

    # 2. Get item description bg mask in bad
    vertical_mask = get_item_description_bg_mask(
        bgr[:, band_left:band_right])

    # 3. Get filled lines within band
    vertical_filled_mask = vertical_mask.sum(
        axis=1) > vertical_mask.shape[1] * .95
    filled_y_values = vertical_filled_mask.nonzero()[0]

    if len(filled_y_values) < 10:
        return None

    # 4. Get item description bg mask on horizontal lines with filled bands
    horizontal_mask = get_item_description_bg_mask(
        bgr[vertical_filled_mask, :])

    # Remove spots with less than 3px width
    horizontal_mask[:, :-2] = np.min(sliding_window_view(
        horizontal_mask, 3, axis=1), axis=2)

    # 5. Find places where non-bg and bg pixels are adjacent
    bg_edges = np.zeros_like(horizontal_mask)
    bg_edges[:, 1:] = np.bitwise_xor(
        horizontal_mask[:, :-1], horizontal_mask[:, 1:])

    # 6. Sum number of edges found on vertical lines
    bg_edges_sums = bg_edges.sum(axis=0)

    if bg_edges_sums.max() < 40:
        return None

    left = cursor[0] - np.flip(bg_edges_sums[:cursor[0]]).argmax()
    right = cursor[0] + bg_edges_sums[cursor[0]:].argmax()

    if right - left < 100:
        return None

    # 7. Find top and bottom
    horizontal_filled_lines = horizontal_mask[:, left:right].sum(
        axis=1) > (right - left) * .95

    top = filled_y_values[horizontal_filled_lines.argmax()]
    bottom = filled_y_values[len(filled_y_values) -
                             np.flip(horizontal_filled_lines).argmax() - 1]

    if bottom - top < 50:
        return None

    # 8. Done
    return left, top, right, bottom
