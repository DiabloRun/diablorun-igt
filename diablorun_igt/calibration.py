import numpy as np

RECTS_1920_1080 = {
    'head': [1527, 108, 1640, 221],
    'primary_left': [1310, 140, 1423, 362],
    'secondary_left': [1310, 140, 1423, 362],
    'primary_right': [1746, 140, 1859, 362],
    'secondary_right': [1746, 140, 1859, 362],
    'body_armor': [1527, 249, 1640, 419],
    'gloves': [1309, 391, 1422, 504],
    'belt': [1527, 447, 1640, 503],
    'boots': [1745, 391, 1858, 504],
    'amulet': [1663, 206, 1719, 262],
    'ring_left': [1447, 447, 1503, 503],
    'ring_right': [1663, 447, 1719, 503],
    'swap_on_primary_left': [1334, 131, 1337, 134],
    'swap_on_primary_right': [1770, 131, 1773, 134],
    'swap_on_secondary_left': [1396, 131, 1399, 134],
    'swap_on_secondary_right': [1832, 131, 1835, 134],
}

RECTS_1366_768 = {
    'head': [1086, 77, 1166, 157],
    'primary_left': [932, 99, 1012, 257],
    'secondary_left': [932, 99, 1012, 257],
    'primary_right': [1242, 99, 1322, 257],
    'secondary_right': [1242, 99, 1322, 257],
    'body_armor': [1086, 177, 1166, 298],
    'gloves': [932, 278, 1012, 358],
    'belt': [1087, 318, 1167, 358],
    'boots': [1242, 278, 1322, 358],
    'amulet': [1184, 146, 1224, 186],
    'ring_left': [1029, 318, 1069, 358],
    'ring_right': [1184, 318, 1224, 358],
    'swap_on_primary_left': [949, 92, 952, 95],
    'swap_on_primary_right': [1259, 92, 1262, 95],
    'swap_on_secondary_left': [993, 92, 996, 95],
    'swap_on_secondary_right': [1303, 92, 1306, 95],
}


def get_calibrated_rects(bgr):
    if bgr.shape[0] == 1080:
        return RECTS_1920_1080
    elif bgr.shape[0] == 768:
        return RECTS_1366_768
