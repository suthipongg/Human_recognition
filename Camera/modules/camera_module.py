import sys
from pathlib import Path
import cv2
import time
ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

class CameraModule:
    def __init__(self):
        # self.cam  = cv2.VideoCapture(0)
        self.cam  = cv2.VideoCapture('/home/mew_ubuntu/Desktop/Attra/Object_tracking/Camera/modules/test.mp4')
        if (self.cam .isOpened() == False):  
            raise Exception("Error reading video file")

    def camera_is_opened(self):
        return self.cam.isOpened()

    def read_camera(self):
        ret, frame = self.cam.read()
        time.sleep(0.05)
        if ret:
            return frame
        return None

if __name__ == "__main__":
    cam = CameraModule()
    cam_open = cam.camera_is_opened()
    frame = cam.read_camera()
    print(cam_open)
    print(frame)
    print(frame.shape)