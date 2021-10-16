import tkinter
import threading
import queue

from .live_split_client import LiveSplitClient
from .diablo_run_client import DiabloRunClient


class GUI:
    def __init__(self):
        self.tk = tkinter.Tk()
        self.tk.title("Diablo.run IGT")

        self.d2r_window_status = tkinter.StringVar()
        self.d2r_window_status.set("D2R window: not detected")
        d2r_window_status_label = tkinter.Label(
            self.tk, textvariable=self.d2r_window_status)
        d2r_window_status_label.pack()

        self.ls_client_status = tkinter.StringVar()
        self.ls_client_status.set("LiveSplit Server: not connected")
        ls_client_status_label = tkinter.Label(
            self.tk, textvariable=self.ls_client_status)
        ls_client_status_label.pack()

        self.ls_client = LiveSplitClient()
        self.dr_client = DiabloRunClient()

    def update(self):
        # Handle state changes
        while True:
            try:
                change = self.dr_client.changes.get_nowait()

                if change["event"] == "is_loading_change":
                    if change["value"]:
                        self.ls_client.pause()
                    else:
                        self.ls_client.unpause()
            except queue.Empty:
                break

        # Update gui elements
        self.d2r_window_status.set(
            "D2R window: " + (self.dr_client.capture_failed and "not detected" or "detected"))

        self.ls_client_status.set(
            "LiveSplit Server: " + (self.ls_client.connected and "connected" or "not connected"))

        self.tk.after(1000//60, self.update)

    def run(self):
        # Start LiveSplit client thread
        ls_client_thread = threading.Thread(target=self.ls_client.run)
        ls_client_thread.start()

        # Start DiabloRun client thread
        dr_client_thread = threading.Thread(target=self.dr_client.run)
        dr_client_thread.start()

        # Start main loop
        self.tk.after(0, self.update)
        self.tk.mainloop()

        # Clean up after GUI is closed
        self.ls_client.stop()
        self.dr_client.stop()

        ls_client_thread.join()
        dr_client_thread.join()
