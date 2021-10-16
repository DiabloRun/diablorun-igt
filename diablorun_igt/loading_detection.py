import numpy as np

BLACK_COLOR_THRESHOLD = 10


def get_horizontal_means(rgb, height):
    return rgb[height:height+1, :, :].mean(axis=2).flatten()


def get_vertical_means(rgb, position):
    return rgb[:, position:position+1, :].mean(axis=2).flatten()


def get_horizontal_black_margin(rgb, height):
    means = get_horizontal_means(rgb, height)
    black_mask = means > BLACK_COLOR_THRESHOLD

    return black_mask.argmax(), np.flip(black_mask).argmax()


def get_vertical_black_margin(rgb, position):
    means = get_vertical_means(rgb, position)
    black_mask = means > BLACK_COLOR_THRESHOLD

    return black_mask.argmax(), np.flip(black_mask).argmax()


def equal_within(a, b, epsilon):
    return abs(a - b) < epsilon


def is_loading(rgb):
    height, width, _channels = rgb.shape
    top, bottom = get_vertical_black_margin(rgb, width // 2)
    left, right = get_horizontal_black_margin(rgb, height // 2)

    # If middle lines are black then this could be logo loading screen
    if top == 0 and bottom == 0 and left == 0 and right == 0:
        logo_top, logo_bottom = get_vertical_black_margin(
            rgb, int(width * 0.92))
        logo_left, logo_right = get_horizontal_black_margin(
            rgb, int(height * 0.88))

        return equal_within(logo_top/height, 0.82, 0.03) and \
            equal_within(logo_bottom/height, 0.1, 0.03) and \
            equal_within(logo_left/width, 0.9125, 0.03) and \
            equal_within(logo_right/width, 0.045, 0.03)

    # If there is a box with a specific size in the middle then this could be door loading screen
    sizes = (top/height, bottom/height, (width - left - right)/height)

    if equal_within(sizes[0], 0.25, 0.03) and equal_within(sizes[1], 0.25, 0.03) and \
            equal_within(sizes[2], 0.738, 0.03):
        return True

    # Check legacy load screen
    return equal_within(sizes[0], 0.286, 0.03) and equal_within(sizes[1], 0.286, 0.03) and \
        equal_within(sizes[2], 0.427, 0.03)
