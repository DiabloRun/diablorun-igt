import os
import threading
import configparser

from diablorun_igt.live_split_client import LiveSplitClient
from diablorun_igt.diablo_run_client import DiabloRunClient
from diablorun_igt.gui import GUI

# Load configuration
config = configparser.ConfigParser()
config.read("diablorun.ini")

is_loading_output = config.get("debug", "is_loading_output", fallback=None)
print("is_loading_output", is_loading_output)

if is_loading_output:
    os.makedirs(is_loading_output, exist_ok=True)

# Start LiveSplit client thread
ls_client = LiveSplitClient()
ls_client_thread = threading.Thread(target=ls_client.run)
ls_client_thread.start()

# Start DiabloRun client thread
dr_client = DiabloRunClient(is_loading_output)
dr_client_thread = threading.Thread(target=dr_client.run)
dr_client_thread.start()

# Start GUI
gui = GUI(ls_client, dr_client)
gui.run()

# Clean up after GUI is closed
ls_client.stop()
dr_client.stop()

ls_client_thread.join()
dr_client_thread.join()
