import numpy as np
from PIL import Image
import glob
import cv2
import time
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


def get_rgb(image_path):
    image = Image.open(image_path)
    return np.array(image)[..., :3]


if __name__ == "__main__":
    # Generate test set
    test_images = glob.glob("test_images/stats/*.png")

    print(test_images)

    for image_path in test_images:
        image = get_rgb(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.threshold(
            image, 125, 255, cv2.THRESH_BINARY)[1]
        # image = cv2.threshold(
        #    image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        #kernel = np.ones((5, 5), np.uint8)
        #image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        #image = cv2.Canny(image, 100, 200)
        #kernel = np.ones((10, 10), np.uint8)
        #cv2.dilate(image, kernel, iterations=1)

        data = pytesseract.image_to_data(image)
        print(data)

        cv2.imwrite("test.png", image)
