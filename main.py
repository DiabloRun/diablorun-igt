import os
import sys
import time
import threading
import configparser

if sys.platform == "win32":
    import global_hotkeys

from diablorun_igt.live_split_client import LiveSplitClient
from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.gui import GUI
from diablorun_igt.utils import save_rgb

# Load configuration
config = configparser.ConfigParser()
config.read("diablorun.ini")

# Start LiveSplit client thread
ls_client = LiveSplitClient()
ls_client_thread = threading.Thread(target=ls_client.run)
ls_client_thread.start()

# Start DiabloRun client thread
api_url = config.get("diablorun", "api_url", fallback="https://api.diablo.run")
api_key = config.get("diablorun", "api_key", fallback=None)

dr_client = DiabloRunClient(api_url, api_key)
dr_client_thread = threading.Thread(target=dr_client.run)
dr_client_thread.start()

# Set up hotkeys
if sys.platform == "win32":
    screenshot_hotkey = config.get("debug", "screenshot_hotkey", fallback=None)
    screenshot_dir = config.get(
        "debug", "screenshot_dir", fallback="screenshots/")

    def save_screenshot():
        if dr_client.bgr is not None and dr_client.cursor is not None:
            save_rgb(dr_client.bgr, os.path.join(screenshot_dir, str(time.time(
            )) + "_" + str(dr_client.cursor[0]) + "_" + str(dr_client.cursor[1]) + ".png"))

    if screenshot_hotkey:
        os.makedirs(screenshot_dir, exist_ok=True)
        global_hotkeys.register_hotkeys([
            [screenshot_hotkey.split(" "), None, save_screenshot]
        ])

        global_hotkeys.start_checking_hotkeys()

# Start GUI
gui = GUI(ls_client, dr_client)
gui.run()

# Clean up after GUI is closed
ls_client.stop()
dr_client.stop()

ls_client_thread.join()
dr_client_thread.join()

if sys.platform == "win32":
    global_hotkeys.stop_checking_hotkeys()
