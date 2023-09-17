import urllib.request
import cv2
import numpy as np

from scripts.object_tracking import Tracking
import torch
import threading

url='http://172.20.10.2/cam.jpg'

det = Tracking()
det.config_model_detection(min_scores=0.4, iou_thres=0.5)
det.config_tracking(max_movement=1000, min_confidence_obj=5, min_out_of_frame=10)

frame=0
sw = 0
last_frame = 0

@torch.no_grad()
def track():
    global frame
    global last_frame
    global sw
    det.select_model_detection("yolo_v6", "l6")
    
    while True:
        if sw == 1:
            if last_frame != frame:
                det.frame = frame
                last_frame = det.frame
                det.reset_data()
                det.detect_and_tracking()
                if det.fps_calculate():
                    break
    print("count :", det.get_amount_person())
    exit()

def request():
    global frame
    global sw
    global last_frame
    while True:
        imgResp = urllib.request.urlopen(url)
        imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        frame = cv2.imdecode(imgNp,-1)
        if sw == 0:
            last_frame = frame
        sw = 1

if __name__ == "__main__":
    x1 = threading.Thread(target=request)
    x2 = threading.Thread(target=track)
    x1.start()
    x2.start()