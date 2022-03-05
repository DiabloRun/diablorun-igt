import cv2
import numpy as np
from tqdm import tqdm
from math import floor


from diablorun_igt.utils import bgr_to_rgb, get_image_ratio_rect, get_image_rect
from diablorun_igt.loading_detection import is_loading
from .template_matching import is_save_and_exit_screen

# S&E screen detection
se_rotator_rect = [(125 - 30)/800, (260 - 30)/600,
                   (125 + 30)/800, (260 + 30)/600]


def get_se_rotator(bgr):
    return cv2.resize(get_image_ratio_rect(bgr, se_rotator_rect), (30, 30))


# Start
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
processed = False


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

    global bgr, manual_active

    cap.set(cv2.CAP_PROP_POS_FRAMES, min(pos, cap_frames - 1))
    manual_active = False

    if paused:
        _, bgr = cap.read()


def create_window():
    cv2.namedWindow(window_name)
    cv2.createTrackbar("Seek", window_name, 0, cap_frames, set_frame)
    cv2.setMouseCallback(window_name, on_mouse_event)


create_window()

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

se_frames = np.zeros(cap_frames, np.uint8)
loading_frames = np.zeros(cap_frames, np.uint8)
manual_frames = np.ones(cap_frames, np.int8) * -1
manual_active = False


def reset_bar():
    global bar
    bar = np.zeros((50, cap_width, 3), np.uint8)
    bar[:, floor(cap_width*start_frame//cap_frames):floor(cap_width*end_frame//cap_frames)] = (255, 0, 0)


def run_gui():
    global start_frame, end_frame, processing, manual_active, paused, bgr

    while True:
        if not paused:
            ret, next_bgr = cap.read()

            if ret:
                bgr = next_bgr
                pos = get_frame(cap)
                cv2.setTrackbarPos("Seek", window_name, pos)

        reset_bar()

        pos = get_frame(cap)
        bgr_rect = get_image_rect(bgr, rect)
        key = cv2.waitKeyEx(1)

        if manual_active and key != -1 and not (key == 2555904 or key == 63235):
            manual_active = False

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
        elif key == ord("o"):
            end_frame = get_frame(cap)
        elif key == ord("l"):
            if manual_frames[pos] == 1:
                manual_frames[pos] = 0
            else:
                manual_frames[pos] = 1
                manual_active = True
        elif paused and (key == 2555904 or key == 63235):
            ret, bgr = cap.read()
            manual_active_prev = manual_active

            pos = get_frame(cap)
            cv2.setTrackbarPos("Seek", window_name, pos)
            manual_active = manual_active_prev

            if manual_active:
                manual_frames[pos] = 1
        elif paused and (key == 2424832 or key == 63234):
            cv2.setTrackbarPos("Seek", window_name, max(0, get_frame(cap) - 2))
            pos = get_frame(cap)
        elif key == 13:  # enter
            processing = True
            break
        elif key != -1:
            print(key)

        # Draw frame
        if manual_frames[pos] == 0:
            cv2.putText(bar, str(pos) + " MANUAL: PLAYING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
        elif manual_frames[pos] == 1:
            cv2.putText(bar, str(pos) + " MANUAL: LOADING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        elif processed and excluded_frames[pos] == 1:
            cv2.putText(bar, str(pos) + " PROCESSED: LOADING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        elif processed and excluded_frames[pos] == 0:
            cv2.putText(bar, str(pos) + " PROCESSED: PLAYING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        elif not processed and is_loading(bgr_rect):
            cv2.putText(bar, str(pos) + " LOADING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        elif not processed and is_save_and_exit_screen(bgr_rect):
            cv2.putText(bar, str(pos) + " S&E (UNKNOWN)", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        else:
            cv2.putText(bar, str(pos) + " PLAYING", (25, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

        frame = np.concatenate((bgr, instructions, bar), 0)
        cv2.rectangle(frame, rect[0:2], rect[2:4], (0, 0, 255), 1)
        cv2.imshow(window_name, frame)

    cv2.destroyAllWindows()


run_gui()

# Process
se_rotator_prev = None

if processing:
    print("Processing...")
    set_frame(start_frame)

    for i in tqdm(range(end_frame - start_frame)):
        ret, bgr = cap.read()
        bgr_rect = get_image_rect(bgr, rect)
        rgb = bgr_to_rgb(bgr_rect)
        se_rotator = get_se_rotator(bgr_rect)

        if is_loading(rgb):
            loading_frames[start_frame+i] = 1
        elif i > 0 and (se_rotator - se_rotator_prev).sum() < 10000 and is_save_and_exit_screen(bgr_rect):
            se_frames[start_frame+i] = 1

        se_rotator_prev = se_rotator

# Fill S&E holes
for i in range(start_frame + 1, end_frame - 1):
    if se_frames[i] == 0 and se_frames[i-1] == 1 and se_frames[i+1] == 1:
        se_frames[i] = 1

# Remove S&E noise
for i in range(start_frame + 1, end_frame - 1):
    if se_frames[i] == 1 and se_frames[i-1] == 0 and se_frames[i+1] == 0:
        se_frames[i] = 0

# Overwrite manual frames
excluded_frames = np.logical_or(se_frames, loading_frames)

for i in range(start_frame + 1, end_frame - 1):
    if manual_frames[i] != -1:
        excluded_frames[i] = manual_frames[i]

# Run GUI again for verification
processed = True
paused = True

create_window()
run_gui()

for i in range(start_frame + 1, end_frame - 1):
    if manual_frames[i] != -1:
        excluded_frames[i] = manual_frames[i]

# Output log
fps = cap.get(cv2.CAP_PROP_FPS)

if processing:
    videolog_path = video_path+"_log.mp4"
    print("Writing video log to " + videolog_path + "...")
    statusbar = np.zeros((50, cap_width, 3), np.uint8)
    videolog = cv2.VideoWriter(
        videolog_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (cap_width, 50 + cap_height))

    set_frame(start_frame)

    for i in tqdm(range(end_frame - start_frame)):
        ret, bgr = cap.read()

        cv2.rectangle(statusbar, (0, 0), (cap_width, 50), (0, 0, 0), -1)

        if excluded_frames[start_frame+i]:
            # if se_frames[start_frame+i]:
            #    cv2.putText(statusbar, "S&E " + str(start_frame + i), (35, 35),
            #                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
            # elif loading_frames[start_frame+i]:
            cv2.putText(statusbar, "LOADING " + str(start_frame + i), (35, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255))
        else:
            cv2.putText(statusbar, "PLAYING " + str(start_frame + i), (35, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

        frame = np.concatenate((statusbar, bgr), 0)
        videolog.write(frame)

    videolog.release()

# Print stats
rta_frames = end_frame - start_frame
igt_frames = rta_frames - excluded_frames[start_frame:end_frame].sum()
rta_seconds = rta_frames / fps
igt_seconds = igt_frames / fps

print("RTA:", rta_frames, "frames,", rta_seconds, "seconds")
print("IGT:", igt_frames, "frames,", igt_seconds, "seconds")

# Done
cap.release()
