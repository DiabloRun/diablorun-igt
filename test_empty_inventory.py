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


if __name__ == "__main__":
    for image_path in glob.glob("test_images/empty_inventory/*.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = get_bgr(image_path)
        empty_slots = inventory_detection.get_empty_item_slots(bgr)

        print(empty_slots)
