import os
import io
import PIL
import glob
import numpy as np
import configparser
import urllib.request

from diablorun_igt.utils import bgr_to_gray, resize_image, load_bgr, save_gray
from diablorun_igt.diablo_run_client import DiabloRunClient

MAX_WIDTH_TO_HEIGHT = 2.11261
MIN_WIDTH_RATIO = 0.318866


def image_to_byte_array(image: PIL.Image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format="jpeg")
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


def send_image(api_url, api_key, image):
    image_bytes = image_to_byte_array(image)
    print(api_url, api_key, len(image_bytes))
    req = urllib.request.Request(
        api_url + "/d2r/image", image_bytes)
    req.add_header('Content-Type', 'application/octet-stream')
    req.add_header('Authorization', 'Bearer ' + api_key)
    res = urllib.request.urlopen(req)

    print("send_image", res.read())


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

        bgr = load_bgr(image_path)

        if bgr.shape[0] > 720:
            bgr = resize_image(bgr, (bgr.shape[1]*720//bgr.shape[0], 720))
        if bgr.shape[1] > 1280:
            bgr = resize_image(bgr, (1280, bgr.shape[0]*1280//bgr.shape[1]))

        gray = PIL.Image.fromarray(
            np.uint8(np.any(bgr < 150, axis=2) * 255), 'L')

        #rect = get_item_description_rect(bgr, cursor, True)

        print(image_name, gray.width, gray.height)

        #save_gray(gray, "debug/test.jpg")
        send_image(api_url, api_key, gray)
        break
