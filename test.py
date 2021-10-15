import numpy as np
from PIL import Image
import glob

from diablorun_igt.detector import Detector

def get_rgb(image_path):
    image = Image.open(image_path)
    return np.array(image)[...,:3]

if __name__ == "__main__":
    # Generate test set
    test_images = []
    
    for image_path in glob.glob("test_images/loading/**/*.png"):
        test_images.append({ "is_loading": True, "path": image_path })

    for image_path in glob.glob("test_images/dark area/*.png"):
        test_images.append({ "is_loading": False, "path": image_path })

    # Test loading detection
    for test_image in test_images:
        image_rgb = get_rgb(test_image["path"])

        detector = Detector(image_rgb)
        is_loading = detector.is_loading()

        if is_loading != test_image["is_loading"]:
            print(test_image["path"], "is_loading", is_loading, "should be", test_image["is_loading"])
