import cv2
import numpy as np
from tqdm import tqdm
from math import floor
from Levenshtein import distance as levenshtein_distance
import pytesseract


from diablorun_igt.utils import bgr_to_rgb, get_image_rect
from diablorun_igt.loading_detection import is_loading

video_path = input("Enter path to video: ")
window_name = "Diablo.run IGT"

cap = cv2.VideoCapture(video_path)
cap_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
ret, bgr = cap.read()
cap_height, cap_width, cap_channels = bgr.shape

rect = [cap_width - cap_height*800//600, 0, cap_width, cap_height]
end = False
paused = True
processing = False


def on_mouse_event(event, x, y, direction, param):
    if not processing and event == cv2.EVENT_MOUSEWHEEL:
        rect[2] = rect[2] + np.sign(direction)
        rect[3] = rect[3] + np.sign(direction)


def move_rect(dx, dy):
    rect[0] = rect[0] + dx
    rect[1] = rect[1] + dy
    rect[2] = rect[2] + dx
    rect[3] = rect[3] + dy


def get_frame(cap):
    return int(cap.get(cv2.CAP_PROP_POS_FRAMES))


def set_frame(pos):
    if get_frame(cap) == pos:
        return

    global bgr

    cap.set(cv2.CAP_PROP_POS_FRAMES, min(pos, cap_frames - 1))

    if paused:
        _, bgr = cap.read()


cv2.namedWindow(window_name)
cv2.createTrackbar("Seek", window_name, 0, cap_frames, set_frame)
cv2.setMouseCallback(window_name, on_mouse_event)

instructions = np.zeros((150, cap_width, 3), np.uint8)
cv2.putText(instructions, "1. Use mousewheel and WASD to resize/move the rect on D2 window", (25, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
cv2.putText(instructions, "2. Use the trackbar and left/right arrows to seek, space to toggle pause", (25, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
cv2.putText(instructions, "3. Press I to mark a frame as the start", (25, 75),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
cv2.putText(instructions, "4. Press O to mark a frame as the end", (25, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
cv2.putText(instructions, "5. Press ENTER to begin processing", (25, 125),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))

bar = np.zeros((50, cap_width, 3), np.uint8)
start_frame = 0
end_frame = cap_frames - 1


def reset_bar():
    global bar
    bar = np.zeros((50, cap_width, 3), np.uint8)
    bar[:, floor(cap_width*start_frame//cap_frames):floor(cap_width*end_frame//cap_frames)] = (255, 0, 0)


reset_bar()

while True:
    if not paused:
        ret, next_bgr = cap.read()

        if ret:
            bgr = next_bgr
            pos = get_frame(cap)
            cv2.setTrackbarPos("Seek", window_name, pos)

    frame = np.concatenate((bgr, instructions, bar), 0)

    cv2.rectangle(frame, rect[0:2], rect[2:4], (0, 0, 255), 1)
    cv2.imshow(window_name, frame)

    key = cv2.waitKeyEx(1)

    if key == ord("q"):
        break
    elif key == 32:  # space
        paused = not paused
    elif key == ord("w"):
        move_rect(0, -1)
    elif key == ord("a"):
        move_rect(-1, 0)
    elif key == ord("s"):
        move_rect(0, 1)
    elif key == ord("d"):
        move_rect(1, 0)
    elif key == ord("i"):
        start_frame = get_frame(cap)
        reset_bar()
    elif key == ord("o"):
        end_frame = get_frame(cap)
        reset_bar()
    elif paused and (key == 2555904 or key == 63235):
        prev_bgr = bgr
        ret, bgr = cap.read()
        cv2.setTrackbarPos("Seek", window_name, get_frame(cap))
    elif paused and (key == 2424832 or key == 63234):
        cv2.setTrackbarPos("Seek", window_name, max(0, get_frame(cap) - 2))
    elif key == 13:  # enter
        processing = True
        break
    elif key != -1:
        print(key)

cv2.destroyAllWindows()

# Process
loading_frames = np.zeros(cap_frames, np.uint8)
rgb_prev = None

if processing:
    set_frame(start_frame)

    for i in tqdm(range(end_frame - start_frame)):
        ret, bgr = cap.read()
        rgb = bgr_to_rgb(get_image_rect(bgr, rect))
        frame_loading = False

        if is_loading(rgb):
            frame_loading = True
        elif i > 0 and (rgb - rgb_prev).mean() < 0.5:
            text_rgb = rgb[int(cap_height*0.4):int(cap_height*0.5),
                           int(cap_width*0.2):int(cap_width*0.8)]

            lines = pytesseract.image_to_string(text_rgb, "D2R").split("\n")

            for line in lines:
                if levenshtein_distance(line, "SAVE AND EXIT GAME") < 10:
                    frame_loading = True
                    break

        rgb_prev = rgb

        if frame_loading:
            loading_frames[start_frame+i] = 1
        else:
            loading_frames[start_frame+i] = 0

# Remove noise
# for i in range(start_frame + 1, end_frame - 1):
#    if loading_frames[i] == 1 and loading_frames[i-1] == 0 and loading_frames[i+1] == 0:
#        loading_frames[i] = 0

# Print stats
fps = cap.get(cv2.CAP_PROP_FPS)

rta_frames = end_frame - start_frame
igt_frames = rta_frames - int(loading_frames[start_frame:end_frame].sum())
rta_seconds = rta_frames / fps
igt_seconds = igt_frames / fps

print("RTA:", rta_frames, "frames,", rta_seconds, "seconds")
print("IGT:", igt_frames, "frames,", igt_seconds, "seconds")
