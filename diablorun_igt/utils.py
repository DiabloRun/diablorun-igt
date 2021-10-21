import numpy as np
import PIL
import io
import os


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


def save_rgb(bgr, path):
    rgb = bgr_to_rgb(bgr)
    PIL.Image.fromarray(rgb.astype('uint8'), 'RGB').save(path)
    print("saved", path)


def save_gray(values, path):
    rgb = PIL.Image.fromarray(values.astype('uint8'), 'L')
    rgb.save(path)
    print("saved", path)
