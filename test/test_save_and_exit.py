import os
import io
import PIL
import glob
import numpy as np
import cv2

from diablorun_igt.utils import load_bgr, save_gray, save_bgr, get_image_ratio_rect

if __name__ == "__main__":
    se_rotator_rect = [(125 - 30)/800, (260 - 30)/600,
                       (125 + 30)/800, (260 + 30)/600]

    templates = [
        cv2.imread("diablorun_video_igt/options_template_dark.png", 0),
        cv2.imread("diablorun_video_igt/options_template_light.png", 0)
    ]
    method = cv2.TM_CCOEFF

    for image_path in glob.glob("test_images/save_and_exit/**.png"):
        image_name = os.path.basename(image_path).split(".")[0]

        bgr = cv2.imread(image_path)
        #bgr = cv2.resize(bgr, (426, 320))
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # rgb = bgr_to_rgb(bgr[int(bgr.shape[0]*0.4):int(bgr.shape[0]*0.5),
        #                     int(bgr.shape[1]*0.2):int(bgr.shape[1]*0.8)])

        for template in templates:
            template_cp = cv2.resize(template, (int(
                gray.shape[1]/800*template.shape[1]), int(gray.shape[0]/800*template.shape[0])))
            res = cv2.matchTemplate(gray, template_cp, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc

            bottom_right = (top_left[0] + template_cp.shape[1],
                            top_left[1] + template_cp.shape[0])

            print(abs(top_left[0] / gray.shape[1] - 0.4) < 0.05 and
                  abs(top_left[1]/gray.shape[0] - 0.33125) < 0.05)

            cv2.rectangle(bgr, top_left, bottom_right, (255, 0, 0), 2)

        se_rotator = get_image_ratio_rect(bgr, se_rotator_rect)
        print(se_rotator.mean())
        cv2.rectangle(bgr, (int(se_rotator_rect[0]*bgr.shape[1]), int(se_rotator_rect[1]*bgr.shape[0])),
                      (int(se_rotator_rect[2]*bgr.shape[1]), int(se_rotator_rect[3]*bgr.shape[0])), (0, 0, 255), 2)
        save_bgr(bgr, "debug/" + image_name + ".png")

        #gray = np.uint8(np.any(rgb < 100, axis=2) * 255)
        #gray = cv2.erode(gray,  np.ones((4, 4), 'uint8'), iterations=1)

        # if image_name == "2":
        #    save_gray(gray, "debug/test.jpg")

        #lines = pytesseract.image_to_string(rgb, "D2R").split("\n")

        # for line in lines:
        #    print(image_name, levenshtein_distance(
        #        line, "SAVE AND EXIT GAME"))

# 125/800, 256/600
