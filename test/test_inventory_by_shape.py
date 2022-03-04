import os
import numpy as np
from PIL import Image
import glob
import configparser
import time

from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.utils import bgr_to_gray, bgr_to_hs, bgr_to_hsl, bgr_to_hue, bgr_to_rgb, get_jpg, save_gray, save_bgr, save_rgb
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
        cursor = [int(x) for x in image_name.split("_")[-2:]]

        write_docs = image_name == "axe_2704_757"
        #write_docs = image_name == "talrasha_1609_341"
        #write_docs = image_name == "hover_gloves_1388_441"
        write_docs = image_name == "ring_left_2885_1035"
        #write_docs = image_name == "axe_2704_757"

        if not write_docs:
            continue
        
        bgr = get_bgr(image_path)

        start = time.time()
        rect = inventory_detection.get_item_description_rect(bgr, cursor, write_docs)
        print(time.time() - start)

        if rect is None:
            print("skip", image_name)
            continue

        # Done
        left, top, right, bottom = rect

        bgr[top:bottom, left-2:left] = (0, 255, 255)
        bgr[top:bottom, right:right+2] = (0, 255, 255)
        bgr[top-2:top, left:right] = (0, 255, 255)
        bgr[bottom:bottom+2, left:right] = (0, 255, 255)

        save_bgr(bgr, "debug/" + image_name + ".jpg")
