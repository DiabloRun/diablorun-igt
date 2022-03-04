import os
import io
import PIL
import glob
import numpy as np
import pytesseract
import cv2

from diablorun_igt.utils import bgr_to_gray, resize_image, load_bgr, save_gray
from diablorun_igt.diablo_run_client import DiabloRunClient

if __name__ == "__main__":
    for image_path in glob.glob("test_images/save_and_exit/**.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = load_bgr(image_path)
        bgr = bgr[int(bgr.shape[0]*0.4):int(bgr.shape[0]*0.5),
                  int(bgr.shape[1]*0.2):int(bgr.shape[1]*0.8)]

        gray = np.uint8(
            np.all(bgr - np.array((141, 130, 100)) < 5, axis=2) * 255)
        gray = cv2.erode(gray,  np.ones((4, 4), 'uint8'), iterations=1)
        #gray = cv2.dilate(gray,  np.ones((3, 3), 'uint8'), iterations=2)

        img_gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)
        edges = cv2.dilate(edges,  np.ones((3, 3), 'uint8'), iterations=1)
        edges = cv2.erode(edges,  np.ones((4, 4), 'uint8'), iterations=1)

        # 8d8264

        if image_name == "5":
            save_gray(edges, "debug/test.jpg")
        print(image_name, pytesseract.image_to_string(gray))

        # break
