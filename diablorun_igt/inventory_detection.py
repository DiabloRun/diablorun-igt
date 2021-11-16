import cv2
import numpy as np

from diablorun_igt.utils import bgr_to_hs, get_image_rect, save_bgr, save_gray


# BGR
ITEM_DESCRIPTION_BG_COLOR = np.array((2, 2, 2))
ITEM_SLOT_COLOR = np.array((2, 2, 2))
ITEM_HOVER_COLOR = np.array((10, 30, 6))
EMPTY_SLOT_COLOR = np.array((20, 20, 20))
DARK_BG_THRESHOLD = 15

TEXT_COLORS = (
    (86, 136, 158),
    (113, 113, 113),
    (127, 184, 203),
    (255, 255, 255),
    (255, 118, 118),
    (0, 255, 0),
    (85, 85, 255)
)

TEXT_COLORS_HS = (
    (240, 100),
    (60, 100),
    #(0, 100),
    (42, 30),
    (120, 100),
    #(0, 0),
)

# rgb(170, 137, 255)
# rgb(170, 147, 255)

ITEM_SLOTS = ('head', 'primary_left', 'primary_right', 'secondary_left', 'secondary_right',
              'body_armor', 'gloves', 'belt', 'boots', 'amulet', 'ring_left', 'ring_right')

ITEM_SLOT_EMPTY_CENTER = {
    'head': ((26, 26, 25), 2),
    'primary_left': ((13, 13, 13), 2),
    'primary_right': ((13, 13, 13), 2),
    'secondary_left': ((13, 13, 13), 2),
    'secondary_right': ((13, 13, 13), 2),
    'body_armor': ((28, 29, 28), 6),
    'gloves': ((18, 18, 17), 3),
    'belt': ((36, 36, 36), 12),
    'boots': ((25, 24, 23), 4),
    'amulet': ((16, 15, 15), 3),
    'ring_left': ((29, 29, 28), 3),
    'ring_right': ((29, 29, 28), 3)
}


def get_item_slot_rects(calibration, bgr):
    swap = get_swap(calibration, bgr)
    rects = calibration["item_slot_rects"].copy()

    if swap == "secondary":
        del rects["primary_left"]
        del rects["primary_right"]
    else:
        del rects["secondary_left"]
        del rects["secondary_right"]

    return rects


def get_hovered_item_slot(calibration, bgr, cursor):
    if cursor is None:
        return None

    rects = get_item_slot_rects(calibration, bgr)

    if rects is None:
        return None

    for slot in rects:
        l, t, r, b = rects[slot]

        if cursor[0] >= l and cursor[0] <= r and cursor[1] >= t and cursor[1] <= b:
            return ("character", slot), rects[slot]


def is_item_rect_highlighted(bgr, item_rect):
    l, t, r, b = item_rect

    slot_corner_colors = np.array((
        bgr[t+1, l+1],
        bgr[t+1, r-1],
        bgr[b-1, l+1],
        bgr[b-1, r-1]
    ))

    return np.sum(np.all(np.abs(slot_corner_colors - ITEM_HOVER_COLOR) < 10, axis=1)) > 1


def is_inventory_open(calibration, bgr):
    return (get_image_rect(bgr, calibration["inventory_text_rect"]) == calibration["inventory_text_bgr"]).all()


def get_swap(calibration, bgr):
    primary_brightness = get_image_rect(
        bgr, calibration['swap_primary_rect']).mean()
    secondary_brightness = get_image_rect(
        bgr, calibration['swap_secondary_rect']).mean()

    if primary_brightness > secondary_brightness:
        return "primary"

    return "secondary"


def get_empty_item_slots(calibration, bgr):
    rects = get_item_slot_rects(calibration, bgr)
    empty_slots = set()

    for slot in rects:
        if (get_image_rect(bgr, calibration["empty_item_slot_rects"][slot]) == calibration["empty_item_slot_bgr"][slot]).all():
            empty_slots.add(("character", slot))

    return empty_slots


"""
def get_item_description_bg_mask(bgr):
    return np.all(np.abs(bgr - ITEM_DESCRIPTION_BG_COLOR) < 8, axis=2)


def get_item_description_rect(bgr, cursor):
    if cursor is None:
        return None

    # 1. Get band around cursor
    band_left, band_right = cursor[0] - 25, cursor[0] + 25

    # 2. Get item description bg mask in bad
    vertical_mask = get_item_description_bg_mask(
        bgr[:, band_left:band_right])

    # 3. Get filled lines within band
    vertical_filled_mask = vertical_mask.sum(
        axis=1) > vertical_mask.shape[1] * .95
    filled_y_values = vertical_filled_mask.nonzero()[0]

    if len(filled_y_values) < 10:
        return None

    # 4. Get item description bg mask on horizontal lines with filled bands
    horizontal_mask = get_item_description_bg_mask(
        bgr[vertical_filled_mask, :])

    # Remove spots with less than 3px width
    horizontal_mask[:, :-2] = np.min(sliding_window_view(
        horizontal_mask, 3, axis=1), axis=2)

    # 5. Find places where non-bg and bg pixels are adjacent
    bg_edges = np.zeros_like(horizontal_mask)
    bg_edges[:, 1:] = np.bitwise_xor(
        horizontal_mask[:, :-1], horizontal_mask[:, 1:])

    # 6. Sum number of edges found on vertical lines
    bg_edges_sums = bg_edges.sum(axis=0)

    if bg_edges_sums.max() < 40:
        return None

    left = cursor[0] - np.flip(bg_edges_sums[:cursor[0]]).argmax()
    right = cursor[0] + bg_edges_sums[cursor[0]:].argmax()

    if right - left < 100:
        return None

    # 7. Find top and bottom
    horizontal_filled_lines = horizontal_mask[:, left:right].sum(
        axis=1) > (right - left) * .95

    top = filled_y_values[horizontal_filled_lines.argmax()]
    bottom = filled_y_values[len(filled_y_values) -
                             np.flip(horizontal_filled_lines).argmax() - 1]

    if bottom - top < 50:
        return None

    # 8. Done
    return left, top, right, bottom
"""


def get_text_mask(bgr):
    text_mask = np.zeros(bgr.shape[:2], dtype=bool)
    hs = bgr_to_hs(bgr)

    for color in TEXT_COLORS_HS:
        #text_mask = np.bitwise_or(text_mask, np.all(bgr == color, axis=2))
        text_mask = np.bitwise_or(text_mask, np.all(hs == color, axis=2))
    
    return text_mask


# data must be sorted
def get_nn_ranges(data, max_dist):
    groups = []
    group = None

    for x in data:
        if group is None or x - group[1] > max_dist:
            group = [x, x]
            groups.append(group)
            continue

        group[1] = x

    return groups


def text_has_dark_bg(bgr, y_range, x_range):
    return np.sum(np.max(bgr[y_range[0]-2:y_range[1]+2, x_range[0]-2:x_range[1]+2], axis=2) < DARK_BG_THRESHOLD) > (y_range[1] - y_range[0]) * (x_range[1] - x_range[0]) / 4


def get_item_description_text_rect(bgr, center, band_width, min_text_line_width=-1, write_docs=-1):
    band_left, band_right = center - band_width//2, center + band_width//2

    # 0. Grayscale
    gray = np.max(bgr, axis=2) > 80

    if write_docs != -1:
        save_gray(gray * 255, "docs/item_description_detection/step" + str(write_docs) + "_gray.jpg")

    # 1. Get rows of pixels with at least 2px of text color
    #text_mask = get_text_mask(bgr[:, band_left:band_right])
    #text_row_mask = np.sum(text_mask, axis=1) >= 2

    text_row_mask = np.std(gray, axis=1) > 40

    if write_docs != -1:
        bgr_docs = np.copy(bgr)
        bgr_docs[:, band_left:band_right][text_row_mask, :] = (0, 255, 0)

        save_bgr(bgr_docs, "docs/item_description_detection/step" + str(write_docs + 1) + "_text_row_mask.jpg")
    
    # 2. Group rows of pixels to rows of text
    text_row_mask_y = text_row_mask.nonzero()[0]
    text_row_ranges = get_nn_ranges(text_row_mask_y, 5)
    
    if write_docs != -1:
        for i, y_range in enumerate(text_row_ranges):
            bgr_docs[y_range[0]:y_range[1], band_left:band_right] = (i % 2) and (0, 0, 255) or (255, 0, 0)

        save_bgr(bgr_docs, "docs/item_description_detection/step" + str(write_docs + 2) + "_text_rows.jpg")
    
    # 3. Filter groups by background color (at least 25% of pixels in area must be dark)
    text_row_ranges = list(filter(
        lambda y_range: text_has_dark_bg(bgr, y_range, (band_left, band_right)),
        text_row_ranges
    ))

    # There should be at least two separate rows of text for item description
    if len(text_row_ranges) < 2:
        return None
    
    if write_docs != -1:
        bgr_docs = np.copy(bgr)
        
        for i, y_range in enumerate(text_row_ranges):
            bgr_docs[y_range[0]:y_range[1], band_left:band_right] = (i % 2) and (0, 0, 255) or (255, 0, 0)

        save_bgr(bgr_docs, "docs/item_description_detection/step" + str(write_docs + 3) + "_text_rows_with_dark_bg.jpg")

    # 4. Get columns with at least 2px of text color
    left = bgr.shape[1]
    right = 0
    text_col_masks = []

    lefts = []
    rights = []
    centers = []
    tops = []
    bottoms = []

    for y_range in text_row_ranges:
        #text_mask = get_text_mask(bgr[y_range[0]:y_range[1], :])
        #text_col_mask = np.sum(text_mask, axis=0) >= 2
        text_col_mask = np.std(gray[y_range[0]:y_range[1], :], axis=0) > 30

        text_col_mask_x = text_col_mask.nonzero()[0]
        text_col_ranges = get_nn_ranges(text_col_mask_x, 5)

        if write_docs != -1:
            text_col_masks.append(text_col_mask)

        """
        left = None
        right = None

        for x_range in text_col_ranges:
            if text_has_dark_bg(bgr, y_range, x_range):
                #left = min(left, x_range[0])
                left = x_range[0]
                break
        
        for x_range in reversed(text_col_ranges):
            if text_has_dark_bg(bgr, y_range, x_range):
                #right = max(right, x_range[1])
                right = x_range[1]
                break

        if left is None or right is None:
            continue
        """

        if len(text_col_ranges) < 2:
            continue

        left = text_col_ranges[0][0]
        right = text_col_ranges[-1][1]

        if min_text_line_width != -1 and (right - left) < min_text_line_width:
            continue
        
        lefts.append(left)
        rights.append(right)
        centers.append((left + right) // 2)
        tops.append(y_range[0])
        bottoms.append(y_range[1])
    
    if len(centers) == 0:
        return None

    # Get vertical edges
    top = tops[0]
    bottom = bottoms[-1]

    # Remove horizontal outliers
    centers = np.array(centers)
    without_outliers = np.abs(centers - centers.mean()) <= centers.std()

    if without_outliers.sum() < 1:
        return None
    
    left = np.array(lefts)[without_outliers].min()
    right = np.array(rights)[without_outliers].max()

    if write_docs != -1:
        for i in range(len(text_row_ranges)):
            y0, y1 = text_row_ranges[i]
            bgr_docs[y0:y1, text_col_masks[i]] = (0, 0, 255)
        
        save_bgr(bgr_docs, "docs/item_description_detection/step" + str(write_docs + 4) + "_text_col_mask.jpg")
    
    # 5. Done
    if write_docs != -1:
        bgr_docs[top:bottom, left-2:left] = (0, 255, 255)
        bgr_docs[top:bottom, right:right+2] = (0, 255, 255)
        bgr_docs[top-2:top, left:right] = (0, 255, 255)
        bgr_docs[bottom:bottom+2, left:right] = (0, 255, 255)

        save_bgr(
            bgr_docs, "docs/item_description_detection/step" + str(write_docs + 5) + "_rect.jpg")
    
    return left, top, right, bottom


"""
def get_item_description_rect(bgr, cursor, write_docs=False):
     # Find item description horizontal center using a narrow band
        rect = get_item_description_text_rect(bgr, cursor[0], 20, -1, not write_docs and -1 or 0)

        if rect is None:
            return None

        center = (rect[0] + rect[2]) // 2

        # Find whole item description rect using a band around the center
        rect = get_item_description_text_rect(bgr, center, 30, 25, not write_docs and -1 or 5)

        if rect is None:
            return None

        # Add padding
        return (
            rect[0] - 10,
            rect[1] - 10,
            rect[2] + 10,
            rect[3] + 10
        )
"""


def get_item_description_rect(bgr, cursor, write_docs=False):
    resized = cv2.resize(bgr, (bgr.shape[1] * 720 // bgr.shape[0], 720))
    resized_cursor = np.array(cursor) * resized.shape[:2] // bgr.shape[:2]
    
    kernel_size = 5

    mask = (resized.max(-1) < DARK_BG_THRESHOLD).astype(np.uint8)
    mask = cv2.erode(mask, np.ones((kernel_size, kernel_size), np.uint8))

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    largest_contour = None
    largest_contour_size = None

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if w < 100 or h < 50:
            continue

        if x > resized_cursor[0] or x + w < resized_cursor[0]:
            continue

        contour_size = h * w

        if largest_contour is None or contour_size > largest_contour_size:
            largest_contour = contour
            largest_contour_size = contour_size

        if write_docs:
            resized[y:y+h, x:x+w] = (255, 0, 0)

    if largest_contour is None:
        return None

    x_median, y_median = np.median(largest_contour, axis=0)[0]
    top_half = largest_contour[:,:,1] < y_median
    bottom_half = largest_contour[:,:,1] > y_median
    left_half = largest_contour[:,:,0] < x_median
    right_half = largest_contour[:,:,0] > x_median

    top = np.argmax(np.bincount(largest_contour[top_half][:,1]))
    bottom = np.argmax(np.bincount(largest_contour[bottom_half][:,1]))
    left = np.argmax(np.bincount(largest_contour[left_half][:,0]))
    right = np.argmax(np.bincount(largest_contour[right_half][:,0]))

    if write_docs:
        resized[top:bottom, left:right] = (0, 0, 255)
        cv2.drawContours(resized, contours, -1, (0,255,0), 3)
        save_bgr(resized, "docs/item_description_detection/cv.jpg")
    
    return (
        left * bgr.shape[1] // resized.shape[1],
        top * bgr.shape[0] // resized.shape[0],
        right * bgr.shape[1] // resized.shape[1],
        bottom * bgr.shape[0] // resized.shape[0]
    )
