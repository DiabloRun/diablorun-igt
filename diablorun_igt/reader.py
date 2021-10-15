import mss
import mss.tools
import numpy as np

from .window import Window
from .detector import Detector

class Reader:
    is_loading = False

    def __init__(self):
        self.window = Window()
        self.sct = mss.mss()
    
    def get_changes(self):
        changes = []

        rect = self.window.get_rect()
        screenshot = self.sct.grab(rect)
        #mss.tools.to_png(screenshot.rgb, screenshot.size, output="grab.png")
        rgb = np.array(screenshot)[...,:3]

        detector = Detector(rgb)
        new_is_loading = detector.is_loading()

        if new_is_loading != self.is_loading:
            changes.append({ "event": "is_loading", "value": new_is_loading })
            self.is_loading = new_is_loading
        
        return changes
    
    def close(self):
        self.sct.close()
