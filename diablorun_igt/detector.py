import numpy as np

class Detector:
    BLACK_COLOR_THRESHOLD = 10

    def __init__(self, rgb):
        self.rgb = rgb
        self.height, self.width = self.rgb.shape[:2]
        self.vertical_middle = self.rgb.shape[0] // 2
        self.horizontal_middle = self.rgb.shape[1] // 2
    
    def _get_horizontal_means(self, height):
        return self.rgb[height:height+1,:,:].mean(axis=2).flatten()
    
    def _get_vertical_means(self, position):
        return self.rgb[:,position:position+1,:].mean(axis=2).flatten()
    
    def _get_horizontal_black_margin(self, height):
        means = self._get_horizontal_means(height)
        black_mask = means > self.BLACK_COLOR_THRESHOLD

        return black_mask.argmax(), np.flip(black_mask).argmax()
    
    def _get_vertical_black_margin(self, position):
        means = self._get_vertical_means(position)
        black_mask = means > self.BLACK_COLOR_THRESHOLD

        return black_mask.argmax(), np.flip(black_mask).argmax()
    
    def _equal_within(self, a, b, epsilon):
        return abs(a - b) < epsilon

    def is_loading(self):
        top, bottom = self._get_vertical_black_margin(self.horizontal_middle)
        left, right = self._get_horizontal_black_margin(self.vertical_middle)
        
        # If middle lines are black then this could be logo loading screen
        if top == 0 and bottom == 0 and left == 0 and right == 0:
            logo_top, logo_bottom = self._get_vertical_black_margin(int(self.width * 0.92))
            logo_left, logo_right = self._get_horizontal_black_margin(int(self.height * 0.88))

            return self._equal_within(logo_top/self.height, 0.82, 0.03) and \
                self._equal_within(logo_bottom/self.height, 0.1, 0.03) and \
                self._equal_within(logo_left/self.width, 0.9125, 0.03) and \
                self._equal_within(logo_right/self.width, 0.045, 0.03)
    
        # If there is a box with a specific size in the middle then this could be door loading screen
        return self._equal_within(top/self.height, 0.25, 0.03) and \
            self._equal_within(bottom/self.height, 0.25, 0.03) and \
            self._equal_within((self.width - left - right)/self.height, 0.738, 0.03)
