import os
import numpy as np
from PIL import Image
import glob
import configparser
import io
import json
import base64
from urllib import request, parse

from diablorun_igt.inventory_detection import get_item_description_rect, get_item_slot_hover, get_item_slot_rects
from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.utils import bgr_to_rgb, get_jpg


def get_bgr(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def save_rgb(bgr, path):
    rgb = Image.fromarray(bgr[:, :, ::-1].astype('uint8'), 'RGB')
    rgb.save(path)
    print("saved", path)


def save_grayscale(values, path):
    rgb = Image.fromarray(values.astype('uint8'), 'L')
    rgb.save(path)
    print("saved", path)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("diablorun.ini")
    api_url = config.get("diablorun", "api_url",
                         fallback="https://api.diablo.run")
    api_key = config.get("diablorun", "api_key", fallback=None)
    dr_client = DiabloRunClient(api_url, api_key)

    print(api_url, api_key)

    for image_path in glob.glob("test_images/inventory/**.png"):
        image_name = os.path.basename(image_path)
        bgr = get_bgr(image_path)

        rects = get_item_slot_rects(bgr)
        slot = get_item_slot_hover(bgr, rects)

        if slot != None:
            item_rect = rects[slot]
            description_rect = left, top, right, bottom = get_item_description_rect(
                bgr, rects[slot])
            save_rgb(bgr[top:bottom, left:right], image_name + "_inv.png")

            data = bytes('{ "container": "character", "slot": "' +
                         slot + '", "item_jpg": "', "ascii")
            data += base64.b64encode(get_jpg(bgr, item_rect).getbuffer())
            data += bytes('", "description_jpg": "', "ascii")
            data += base64.b64encode(get_jpg(bgr,
                                     description_rect).getbuffer())
            data += bytes('" }', "ascii")

            req = request.Request(api_url + "/d2r/item", data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', 'Bearer ' + api_key)
            res = request.urlopen(req)
            print(res.read())
