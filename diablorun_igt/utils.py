import numpy as np


def bgr_to_rgb(bgr):
    return bgr[:, :, ::-1]


def bgr_to_gray(bgr):
    return np.dot(bgr, [0.1140, 0.5870, 0.2989])
