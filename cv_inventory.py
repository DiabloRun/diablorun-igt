import os
import numpy as np
from PIL import Image
import glob
import configparser
import time
import cv2

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

        write_docs = image_name == "zephyr_1807_415"

        if not write_docs:
            #continue
            pass
        
        bgr = get_bgr(image_path)

        start = time.time()

        rect = inventory_detection.get_item_description_rect(bgr, cursor, write_docs)

        """
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]
        gray = cv2.blur(gray, (10, 10))
        edges = cv2.Canny(gray, 100, 200)
        #denoise = cv2.fastNlMeansDenoising(edges)

        kernel = np.ones((2,2 ),np.uint8)
        opening = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)

        kernel = np.ones((5,5), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)
        
        yuv = cv2.cvtColor(resized, cv2.COLOR_BGR2YUV)
        yuv[:,:,0] = 255

        print(resized.shape)

        cropped = resized[:, resized_cursor[0] - 25 : resized_cursor[0] + 25]

        #blur = cv2.blur(yuv, (10, 10))


        text_rects, draw, text_chain_bbs = cv2.text.detectTextSWT(cropped, False)

        text_lines = []
        text_rects = list(text_chain_bbs[0])
        text_rects.sort(key=lambda text_rect: text_rect[1])

        for text_rect in text_rects:
            x, y, w, h = text_rect

            if h < 8:
                continue

            if len(text_lines) == 0 or y > text_lines[-1][1]:
                text_lines.append([y, y+h])
                continue
            
            text_lines[-1][1] = max(text_lines[-1][1], y + h)

        #for text_line in text_lines:
        #y0, y1 = text_lines[0][0], text_lines[-1][1]
        #text_rects, draw, text_chain_bbs = cv2.text.detectTextSWT(resized[y0:y1, :], False)

        #for text_rect in text_chain_bbs[0]:
        #    x, y, w, h = text_rect
        #    docs_bgr[y0+y:y0+y+h, x:x+w] = (255, 0, 0)
        """
        
        #print(hist, contour.shape, contour[top_half].shape, contour[:,0,0].shape)

        #print(contour)


        print(time.time() - start)

        """
        for text_rect in text_chain_bbs[0]:
            x, y, w, h = text_rect
            cropped[y:y+h, x:x+w] = (255, 0, 0)
        
        for text_line in text_lines:
            y0, y1 = text_line
            cropped[y0:y1, :] = (0, 0, 255)
        """

        #save_bgr(yuv, "docs/item_description_detection/step2_yuv.jpg")
        #save_bgr(cropped, "docs/item_description_detection/step2_cropped.jpg")
        #save_gray(mask * 255, "docs/item_description_detection/step2_mask.jpg")

        #save_gray(gray, "docs/item_description_detection/step1_blur.jpg")
        #save_gray(thresh, "docs/item_description_detection/step2_thresh.jpg")
        #save_gray(morph, "docs/item_description_detection/step3_morph.jpg")
        #save_gray(opening, "docs/item_description_detection/step2_opening.jpg")
        #save_gray(edges, "docs/item_description_detection/step2_canny.jpg")

        # Done
        if rect is None:
            print("skip", image_name)
        else:
            left, top, right, bottom = rect
            
            bgr[top:bottom, left-1:left] = (0, 255, 255)
            bgr[top:bottom, right:right+1] = (0, 255, 255)
            bgr[top-1:top, left:right] = (0, 255, 255)
            bgr[bottom:bottom+1, left:right] = (0, 255, 255)

        save_bgr(bgr, "debug/" + image_name + ".jpg")
