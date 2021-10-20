import numpy as np
import PIL
import io


def bgr_to_rgb(bgr):
    return bgr[:, :, ::-1]


def bgr_to_gray(bgr):
    return np.dot(bgr, [0.1140, 0.5870, 0.2989])


def get_jpg(bgr, rect=None):
    if rect:
        bgr = bgr[rect[1]:rect[3], rect[0]:rect[2]]

    jpg = io.BytesIO()
    PIL.Image.fromarray(bgr_to_rgb(bgr), "RGB").save(jpg, format="JPEG")

    return jpg
