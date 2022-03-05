import numpy as np
import PIL.Image
import io
import base64


def resize_image(bgr, size):
    image = PIL.Image.fromarray(bgr.astype('uint8'), 'RGB')
    image = image.resize(size, PIL.Image.NEAREST)

    return np.asarray(image)


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


# def get_jpg_b64_buffer(bgr, max_height=None):
#    if max_height and bgr.shape[0] > max_height:
#        bgr = cv2.resize(bgr, (bgr.shape[1]*max_height//bgr.shape[0], max_height))
#
#    return base64.b64encode(get_jpg(bgr).getbuffer())


def save_bgr(bgr, path, rect=None):
    save_rgb(bgr_to_rgb(bgr), path, rect)


def save_rgb(rgb, path, rect=None):
    if not rect is None:
        l, t, r, b = rect
        rgb = rgb[t:b, l:r]

    PIL.Image.fromarray(rgb.astype('uint8'), 'RGB').save(path)
    print("saved", path)


def save_gray(values, path):
    rgb = PIL.Image.fromarray(values.astype('uint8'), 'L')
    rgb.save(path)
    print("saved", path)


def get_image_rect(image, rect):
    if not rect is None:
        l, t, r, b = rect
        return image[t:b, l:r]

    return image


def get_image_ratio_rect(image, ratio_rect):
    if not ratio_rect is None:
        l, t, r, b = ratio_rect
        return image[int(t*image.shape[0]):int(b*image.shape[0]), int(l*image.shape[1]):int(r*image.shape[1])]

    return image


def bgr_in_color_range(bgr, color, dist):
    return np.all(np.abs(bgr - color) <= dist, axis=2)


def load_bgr(image_path):
    image = PIL.Image.open(image_path)
    return np.array(image)[..., :3][:, :, ::-1]


def draw_rect(bgr, rect, color=(0, 0, 255)):
    x0, y0, x1, y1 = rect
    bgr[y0:y1, x0:x0+1] = color
    bgr[y0:y1, x1:x1+1] = color
    bgr[y0:y0+1, x0:x1] = color
    bgr[y1:y1+1, x0:x1] = color


def bgr_to_hs(img):  # (h: 0-255, s: 0-100)
    maxc = img.max(-1)
    minc = img.min(-1)

    out = np.zeros((img.shape[0], img.shape[1], 2), np.uint8)
    #out = np.zeros(img.shape)
    #out[:,:,2] = maxc
    out[:, :, 1] = (maxc-minc) / maxc * 100

    divs = (maxc[..., None] - img) / ((maxc-minc)[..., None])
    cond1 = divs[..., 0] - divs[..., 1]
    cond2 = 2.0 + divs[..., 2] - divs[..., 0]
    h = 4.0 + divs[..., 1] - divs[..., 2]
    h[img[..., 2] == maxc] = cond1[img[..., 2] == maxc]
    h[img[..., 1] == maxc] = cond2[img[..., 1] == maxc]
    out[:, :, 0] = ((h/6.0) % 1.0) * 255

    #out[minc == maxc,:2] = 0
    # print(out)
    return out


def bgr_to_hsl(bgr):  # (h: 0-255, s: 0-100)
    maxc = bgr.max(-1)
    minc = bgr.min(-1)

    divs = (maxc[..., None] - bgr) / ((maxc-minc)[..., None])
    cond1 = divs[..., 0] - divs[..., 1]
    cond2 = 2.0 + divs[..., 2] - divs[..., 0]
    h = 4.0 + divs[..., 1] - divs[..., 2]
    h[bgr[..., 2] == maxc] = cond1[bgr[..., 2] == maxc]
    h[bgr[..., 1] == maxc] = cond2[bgr[..., 1] == maxc]

    out = np.zeros(bgr.shape, np.uint8)
    out[:, :, 0] = ((h/6.0) % 1.0) * 255
    out[:, :, 1] = (maxc-minc) / maxc * 255
    out[:, :, 2] = maxc
    out[minc == maxc, :2] = 0

    return out


def bgr_to_hue(bgr):
    maxc = bgr.max(-1)
    minc = bgr.min(-1)

    divs = (maxc[..., None] - bgr) / ((maxc-minc)[..., None])
    cond1 = divs[..., 0] - divs[..., 1]
    cond2 = 2.0 + divs[..., 2] - divs[..., 0]
    h = 4.0 + divs[..., 1] - divs[..., 2]
    h[bgr[..., 2] == maxc] = cond1[bgr[..., 2] == maxc]
    h[bgr[..., 1] == maxc] = cond2[bgr[..., 1] == maxc]

    return ((h/6.0) % 1.0) * 255
