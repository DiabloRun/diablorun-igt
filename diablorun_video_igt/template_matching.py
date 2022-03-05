import cv2

options_templates = [
    cv2.imread("diablorun_video_igt/options_template_dark.png", 0),
    cv2.imread("diablorun_video_igt/options_template_light.png", 0)
]


def get_template_match(bgr, template, method=cv2.TM_CCOEFF_NORMED):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    template_cp = cv2.resize(template, (int(
        gray.shape[1]/800*template.shape[1]), int(gray.shape[0]/800*template.shape[0])))

    res = cv2.matchTemplate(gray, template_cp, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc

    return top_left[0]/gray.shape[1], top_left[1]/gray.shape[0]


def is_save_and_exit_screen(bgr):
    for template in options_templates:
        top_left = get_template_match(bgr, template)

        if abs(top_left[0] - 0.399) < 0.01 and abs(top_left[1] - 0.33125) < 0.01:
            return True

    return False
