import tkinter
import queue

from .live_split_client import LiveSplitClient
from .diablo_run_client import DiabloRunClient


class GUI:
    def __init__(self, ls_client: LiveSplitClient, dr_client: DiabloRunClient):
        self.tk = tkinter.Tk()
        self.tk.title("Diablo.run IGT")

        self.d2r_window_status = tkinter.StringVar()
        self.d2r_window_status.set("detecting...")

        tkinter.Label(self.tk, text="D2R window:").grid(row=0, column=0)
        tkinter.Label(self.tk, textvariable=self.d2r_window_status).grid(
            row=0, column=1)

        self.ls_client_status = tkinter.StringVar()
        self.ls_client_status.set("connecting...")

        tkinter.Label(self.tk, text="LiveSplit server:").grid(row=1, column=0)
        tkinter.Label(self.tk, textvariable=self.ls_client_status).grid(
            row=1, column=1)

        tkinter.Button(self.tk, text="Calibrate",
                       command=dr_client.calibrate).grid(row=2, column=0)

        self.ls_client = ls_client
        self.dr_client = dr_client

    def update(self):
        # Handle state changes
        while True:
            try:
                change = self.dr_client.changes.get_nowait()
                print(change)

                if change["event"] == "is_loading_change":
                    if change["value"]:
                        self.ls_client.pause()
                    else:
                        self.ls_client.unpause()
            except queue.Empty:
                break

        # Update gui elements
        self.d2r_window_status.set(
            self.dr_client.status + " - " + str(self.dr_client.fps))

        self.ls_client_status.set(
            self.ls_client.connected and "connected" or "not connected")

        self.tk.after(1000//60, self.update)

    def run(self):
        # Start main loop
        self.tk.after(0, self.update)
        self.tk.mainloop()
