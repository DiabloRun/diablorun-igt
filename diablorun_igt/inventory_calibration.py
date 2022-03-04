import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from diablorun_igt.utils import get_image_rect


def get_bottom_borders(bgr, rect, cell_index, count):
    x0, y0, x1, y1 = rect
    cell_width = (x1-x0)//10
    cell_pos = x0 + cell_index * cell_width

    l, r = cell_pos-cell_width//3, cell_pos+cell_width//3
    mask = np.all(bgr[:y0, l:r] > 75, axis=2)
    mask = (mask.sum(axis=1) > mask.shape[1] * .95).astype(int)

    mask = np.min(sliding_window_view(mask, 2), axis=1)
    mask = mask[1:] - mask[:-1] > 0

    y_values = np.flip(mask.nonzero()[0] + 1)[:count]
    max_l_edge = 0
    min_r_edge = bgr.shape[1]

    for y in y_values:
        l_edge = l - np.argmax(np.flip(np.all(bgr[y, :l] <= 40, axis=1)))
        r_edge = r + np.argmax(np.all(bgr[y, r:] <= 40, axis=1))

        max_l_edge = max(max_l_edge, l_edge)
        min_r_edge = min(min_r_edge, r_edge)

    bottom_borders = []

    for y in y_values:
        bottom_borders.append((y, max_l_edge, min_r_edge))

    return bottom_borders


def get_item_rect_by_bottom_border(bottom_border, height_multiplier):
    y1, x0, x1 = bottom_border
    y0 = int(y1 - (x1 - x0) * height_multiplier)
    return x0, y0, x1, y1 - 1


def get_inventory_rects(bgr):
    # 1. Get inventory grid cell color mask
    values = np.all(bgr < 20, axis=2)
    values[:, :values.shape[1]//2] = 0

    # 2. Get box of size 25x25 mask on 1080p
    box_size = 25 * bgr.shape[0] // 1080
    values = np.min(sliding_window_view(values, box_size, axis=1), axis=2)
    values = np.min(sliding_window_view(values, box_size, axis=0), axis=2)

    # 3. Get inventory grid rect
    x0 = np.argmax(values.max(axis=0)) - 1
    y0 = np.argmax(values.max(axis=1)) - 1
    x1 = values.shape[1] - \
        np.argmax(np.flip(values.max(axis=0))) + box_size - 1
    y1 = values.shape[0] - \
        np.argmax(np.flip(values.max(axis=1))) + box_size - 1

    rect = np.array((x0, y0, x1, y1))

    # 4. Get wielded item bottom borders
    gloves_col = get_bottom_borders(bgr, rect, 1, 2)
    ring_left_col = get_bottom_borders(bgr, rect, 3, 1)
    belt_col = get_bottom_borders(bgr, rect, 5, 3)
    ring_right_col = get_bottom_borders(bgr, rect, 7, 2)
    boots_col = get_bottom_borders(bgr, rect, 9, 2)

    # 5a. Get wielded item boxes
    gloves_rect = get_item_rect_by_bottom_border(gloves_col[0], 1)
    primary_left_rect = get_item_rect_by_bottom_border(gloves_col[1], 215/113)
    ring_left_rect = get_item_rect_by_bottom_border(ring_left_col[0], 1)
    belt_rect = get_item_rect_by_bottom_border(belt_col[0], 56/113)
    body_armor_rect = get_item_rect_by_bottom_border(belt_col[1], 170/113)
    head_rect = get_item_rect_by_bottom_border(belt_col[2], 1)
    ring_right_rect = get_item_rect_by_bottom_border(ring_right_col[0], 1)
    amulet_rect = get_item_rect_by_bottom_border(ring_right_col[1], 1)
    boots_rect = get_item_rect_by_bottom_border(boots_col[0], 1)
    primary_right_rect = get_item_rect_by_bottom_border(boots_col[1], 215/113)

    # 5b. Get item swap pixels
    primary_left_center = (
        primary_left_rect[0] + primary_left_rect[2]) // 2

    swap_primary_rect = (
        primary_left_center - 10 - 1, head_rect[1] + 10 - 1,
        primary_left_center - 10 + 1, head_rect[1] + 10 + 1,
    )
    swap_secondary_rect = (
        primary_left_center + 10 - 1, head_rect[1] + 10 - 1,
        primary_left_center + 10 + 1, head_rect[1] + 10 + 1
    )

    # 5c. Get inventory text
    vertical_gap = body_armor_rect[1] - head_rect[3]
    inventory_text_rect = (
        head_rect[0] - vertical_gap,
        #head_rect[1] - int(vertical_gap * 2.5),
        head_rect[1] - vertical_gap * 2 - 1,
        head_rect[2] + vertical_gap,
        head_rect[1] - vertical_gap * 2 + 1
        #head_rect[1] - int(vertical_gap * 1.5)
    )

    calibration = {
        "shape": bgr.shape,

        "inventory_rect": rect,
        "inventory_text_rect": inventory_text_rect,

        "item_slot_rects": {
            "gloves": gloves_rect,
            "primary_left": primary_left_rect,
            "ring_left": ring_left_rect,
            "belt": belt_rect,
            "body_armor": body_armor_rect,
            "head": head_rect,
            "ring_right": ring_right_rect,
            "amulet": amulet_rect,
            "boots": boots_rect,
            "primary_right": primary_right_rect,
            "secondary_left": primary_left_rect,
            "secondary_right": primary_right_rect
        },

        "swap_primary_rect": swap_primary_rect,
        "swap_primary_bgr": get_image_rect(bgr, swap_primary_rect),
        "swap_secondary_rect": swap_secondary_rect,
        "swap_secondary_bgr": get_image_rect(bgr, swap_primary_rect)
    }

    # Get comparison BGRs and empty item slot rects
    calibration["inventory_text_bgr"] = get_image_rect(
        bgr, inventory_text_rect)

    calibration["empty_item_slot_rects"] = {}
    calibration["empty_item_slot_bgr"] = {}

    for slot in calibration["item_slot_rects"]:
        x0, y0, x1, y1 = calibration["item_slot_rects"][slot]
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2

        calibration["empty_item_slot_rects"][slot] = (
            cx - 5, cy - 5, cx + 5, cy + 5)
        calibration["empty_item_slot_bgr"][slot] = get_image_rect(
            bgr, calibration["empty_item_slot_rects"][slot])

    return calibration
