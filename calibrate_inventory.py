import os
import numpy as np
from PIL import Image
import glob
import json
from numpy.lib.npyio import save
from numpy.lib.stride_tricks import sliding_window_view

from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.utils import bgr_in_color_range, bgr_to_gray, bgr_to_rgb, get_image_rect, get_jpg, resize_image, save_gray, save_rgb
from diablorun_igt import inventory_detection


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def draw_rect(bgr, rect, color=(0, 0, 255)):
    x0, y0, x1, y1 = rect
    bgr[y0:y1, x0:x0+1] = color
    bgr[y0:y1, x1:x1+1] = color
    bgr[y0:y0+1, x0:x1] = color
    bgr[y1:y1+1, x0:x1] = color


def get_bottom_borders(bgr, rect, cell_index, count):
    x0, y0, x1, y1 = rect
    cell_width = (x1-x0)//10
    cell_pos = x0 + cell_index * cell_width

    l, r = cell_pos-cell_width//3, cell_pos+cell_width//3
    mask = np.all(bgr[:y0, l:r] > 50, axis=2)
    mask = (mask.sum(axis=1) > mask.shape[1] * .95).astype(int)

    mask = np.min(sliding_window_view(mask, 2), axis=1)
    mask = mask[1:] - mask[:-1] > 0

    y_values = np.flip(mask.nonzero()[0] + 1)[:count]
    max_l_edge = 0
    min_r_edge = bgr.shape[1]

    for y in y_values:
        l_edge = l - np.argmax(np.flip(np.all(bgr[y, :l] <= 40, axis=1)))
        r_edge = r + np.argmax(np.all(bgr[y, r:] <= 40, axis=1))

        bgr[y, l_edge:r_edge] = (0, 255, 255)
        bgr[y, l:r] = (0, 0, 255)

        max_l_edge = max(max_l_edge, l_edge)
        min_r_edge = min(min_r_edge, r_edge)

    bottom_borders = []

    for y in y_values:
        bottom_borders.append((y, max_l_edge, min_r_edge))

    return bottom_borders


def get_item_rect(bottom_border, height_multiplier):
    y1, x0, x1 = bottom_border
    y0 = int(y1 - (x1 - x0) * height_multiplier)
    return x0, y0, x1, y1 - 1


if __name__ == "__main__":
    for image_path in glob.glob("test_images/empty_inventory/*.png"):
        # for image_path in glob.glob("test_images/inventory/test.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = get_bgr(image_path)
        height, width, channels = bgr.shape

        # bgr = resize_image(bgr, (1280, 720))
        # empty_slots = inventory_detection.get_empty_item_slots(bgr)
        # print(empty_slots)

        values = np.all(bgr < 20, axis=2)
        values[:, :values.shape[1]//2] = 0
        save_gray(values * 255, "docs/inventory_calibration/step1.jpg")

        values = np.min(sliding_window_view(values, 25, axis=1), axis=2)
        values = np.min(sliding_window_view(values, 25, axis=0), axis=2)
        save_gray(values * 255, "docs/inventory_calibration/step2.jpg")

        # 3. Get inventory grid rect
        x0 = np.argmax(values.max(axis=0)) - 1
        y0 = np.argmax(values.max(axis=1)) - 1
        x1 = values.shape[1] - np.argmax(np.flip(values.max(axis=0))) + 25 - 1
        y1 = values.shape[0] - np.argmax(np.flip(values.max(axis=1))) + 25 - 1

        rect = np.array((x0, y0, x1, y1))

        draw_rect(bgr, (x0, y0, x1, y1))
        save_rgb(bgr, "docs/inventory_calibration/step3.jpg")

        # 4. Get wielded item bottom borders
        gloves_col = get_bottom_borders(bgr, rect, 1, 2)
        ring_left_col = get_bottom_borders(bgr, rect, 3, 1)
        belt_col = get_bottom_borders(bgr, rect, 5, 3)
        ring_right_col = get_bottom_borders(bgr, rect, 7, 2)
        boots_col = get_bottom_borders(bgr, rect, 9, 2)
        save_rgb(bgr, "docs/inventory_calibration/step4.jpg")

        # 5a. Get wielded item boxes
        gloves_rect = get_item_rect(gloves_col[0], 1)
        draw_rect(bgr, gloves_rect)
        primary_left_rect = get_item_rect(gloves_col[1], 215/113)
        draw_rect(bgr, primary_left_rect)
        ring_left_rect = get_item_rect(ring_left_col[0], 1)
        draw_rect(bgr, ring_left_rect)
        belt_rect = get_item_rect(belt_col[0], 56/113)
        draw_rect(bgr, belt_rect)
        body_armor_rect = get_item_rect(belt_col[1], 170/113)
        draw_rect(bgr, body_armor_rect)
        head_rect = get_item_rect(belt_col[2], 1)
        draw_rect(bgr, head_rect)
        ring_right_rect = get_item_rect(ring_right_col[0], 1)
        draw_rect(bgr, ring_right_rect)
        amulet_rect = get_item_rect(ring_right_col[1], 1)
        draw_rect(bgr, amulet_rect)
        boots_rect = get_item_rect(boots_col[0], 1)
        draw_rect(bgr, boots_rect)
        primary_right_rect = get_item_rect(boots_col[1], 215/113)
        draw_rect(bgr, primary_right_rect)

        # 5b. Get item swap pixels
        primary_left_center = (
            primary_left_rect[0] + primary_left_rect[2]) // 2
        swap_primary = primary_left_center - 10, \
            head_rect[1] + 10
        swap_secondary = primary_left_center + 10, \
            head_rect[1] + 10

        draw_rect(bgr, (
            swap_primary[0] - 1, swap_primary[1] - 1,
            swap_primary[0] + 1, swap_primary[1] + 1
        ), (255, 255, 0))

        draw_rect(bgr, (
            swap_secondary[0] - 1, swap_secondary[1] - 1,
            swap_secondary[0] + 1, swap_secondary[1] + 1
        ), (255, 255, 0))

        # 5c. Get inventory text
        vertical_gap = body_armor_rect[1] - head_rect[3]

        inventory_text_rect = (
            head_rect[0] - vertical_gap, head_rect[1] -
            int(vertical_gap * 2.5),
            head_rect[2] + vertical_gap, head_rect[1] - int(vertical_gap * 1.5)
        )

        draw_rect(bgr, inventory_text_rect)
        inventory_text_b = get_image_rect(bgr, inventory_text_rect)[:, :, 0]
        # print(inventory_text_b.shape)
        # print(json.dumps(inventory_text_b.tolist()))

        # mask = bgr_in_color_range(bgr, (140, 180, 180), 30)

        save_rgb(bgr, "docs/inventory_calibration/step5.jpg")
