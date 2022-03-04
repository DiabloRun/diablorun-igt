import os
import io
import PIL
import glob
import numpy as np
import pytesseract
import cv2
from Levenshtein import distance as levenshtein_distance

from diablorun_igt.utils import load_bgr, save_gray, bgr_to_rgb

if __name__ == "__main__":
    for image_path in glob.glob("test_images/save_and_exit/**.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = load_bgr(image_path)
        rgb = bgr_to_rgb(bgr[int(bgr.shape[0]*0.4):int(bgr.shape[0]*0.5),
                             int(bgr.shape[1]*0.2):int(bgr.shape[1]*0.8)])

        #gray = np.uint8(np.any(rgb < 100, axis=2) * 255)
        #gray = cv2.erode(gray,  np.ones((4, 4), 'uint8'), iterations=1)

        # if image_name == "2":
        #    save_gray(gray, "debug/test.jpg")

        lines = pytesseract.image_to_string(rgb, "D2R").split("\n")

        for line in lines:
            print(image_name, levenshtein_distance(
                line, "SAVE AND EXIT GAME"))

        # break
