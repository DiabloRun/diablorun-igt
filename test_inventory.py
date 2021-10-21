import os
import numpy as np
from PIL import Image
import glob
import configparser
import io
import json
import base64
from urllib import request, parse

from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.utils import bgr_to_rgb, get_jpg, save_rgb
from diablorun_igt import inventory_detection


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def draw_color_overlay(bgr, color):
    bgr[:, :, 0] = color[0]
    bgr[:, :, 1] = color[1]
    bgr[:, :, 2] = color[2]


def mask_to_bgr(mask, color=(255, 255, 255)):
    return np.stack((mask,)*3, axis=-1) * color


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("diablorun.ini")
    api_url = config.get("diablorun", "api_url",
                         fallback="https://api.diablo.run")
    api_key = config.get("diablorun", "api_key", fallback=None)
    dr_client = DiabloRunClient(api_url, api_key)

    for image_path in glob.glob("test_images/item_description/**.png"):
        image_name = os.path.basename(image_path).split(".")[0]
        cursor_x, cursor_y = [int(x) for x in image_name.split("_")[-2:]]

        bgr = get_bgr(image_path)

        write_docs = image_name == "nothing_1700_851"  # "head_1799_286"

        if write_docs:
            bgr_docs = np.copy(bgr)

        # 1. Get band around cursor
        band_left, band_right = cursor_x - 25, cursor_x + 25

        # step 1 docs
        if write_docs:
            bgr_docs[:, (band_left - 1, band_right)] = (255, 0, 0)
            save_rgb(
                bgr_docs, "docs/item_description_detection/step1_vertical_band.jpg")

        # 2. Get item description bg mask in bad
        vertical_mask = inventory_detection.get_item_description_bg_mask(
            bgr[:, band_left:band_right])

        # step 2 docs
        if write_docs:
            bgr_docs[:, band_left:band_right] = mask_to_bgr(vertical_mask)
            save_rgb(
                bgr_docs, "docs/item_description_detection/step2_vertical_bg_mask.jpg")

        # 3. Get filled lines within band
        vertical_filled_mask = vertical_mask.sum(
            axis=1) > vertical_mask.shape[1] * .95
        filled_y_values = vertical_filled_mask.nonzero()[0]

        # step 3 docs
        if write_docs:
            for y in filled_y_values:
                draw_color_overlay(
                    bgr_docs[y:y+1, band_left:band_right], (255, 0, 0))

            save_rgb(
                bgr_docs, "docs/item_description_detection/step3_filled_lines.jpg")

        # 4. Get item description bg mask on horizontal lines with filled bands
        horizontal_mask = inventory_detection.get_item_description_bg_mask(
            bgr[vertical_filled_mask, :])

        # step 4 docs
        if write_docs:
            bgr_docs[vertical_filled_mask, :band_left] = mask_to_bgr(
                horizontal_mask[:, :band_left])
            bgr_docs[vertical_filled_mask, band_right:] = mask_to_bgr(
                horizontal_mask[:, band_right:])

            save_rgb(
                bgr_docs, "docs/item_description_detection/step4_horizontal_bg_mask.jpg")

        # 5. Find places where non-bg and bg pixels are adjacent
        bg_edges = np.zeros_like(horizontal_mask)
        bg_edges[:, 1:] = np.bitwise_xor(
            horizontal_mask[:, :-1], horizontal_mask[:, 1:])

        # step 5 docs
        if write_docs:
            for i, y in enumerate(filled_y_values):
                bgr_docs[y, bg_edges[i].nonzero()] = (0, 255, 0)

            save_rgb(
                bgr_docs, "docs/item_description_detection/step5_horizontal_bg_edges.jpg")

        # 6. Sum number of edges found on vertical lines
        bg_edges_sums = bg_edges.sum(axis=0)

        if bg_edges_sums.max() < 50:
            continue

        left = cursor_x - np.flip(bg_edges_sums[:cursor_x]).argmax()
        right = cursor_x + bg_edges_sums[cursor_x:].argmax()

        # step 6 docs
        if write_docs:
            bgr_docs[:, left-2:left] = (0, 0, 255)
            bgr_docs[:, right:right+2] = (0, 0, 255)

            save_rgb(
                bgr_docs, "docs/item_description_detection/step6_horizontal_max.jpg")

        # 7. Find top and bottom
        horizontal_filled_lines = horizontal_mask[:, left:right].sum(
            axis=1) > (right - left) * .95

        top = filled_y_values[horizontal_filled_lines.argmax()]
        bottom = filled_y_values[len(filled_y_values) -
                                 np.flip(horizontal_filled_lines).argmax() - 1]

        if bottom - top < 50:
            continue

        # step 7 docs
        if write_docs:
            bgr_docs[top-2:top, left:right] = (0, 0, 255)
            bgr_docs[bottom:bottom+2, left:right] = (0, 0, 255)

            save_rgb(
                bgr_docs, "docs/item_description_detection/step7_vertical_edges.jpg")

        # 8. Done
        save_rgb(bgr[top:bottom, left:right],
                 "debug/" + image_name + ".jpg")

        if write_docs:
            bgr_docs[top:bottom, left:right] = bgr[top:bottom, left:right]

            save_rgb(
                bgr_docs, "docs/item_description_detection/step8_done.jpg")
