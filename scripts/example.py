from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    
from scripts.object_tracking import Tracking
from scripts.object_detection import ObjectDetection
from scripts.calculator import CalcFPS
from scripts.manage_media import LoadVideo
import torch

import torch.multiprocessing as mp

@torch.no_grad()
def model():
    obj_det = ObjectDetection()
    obj_det.config_model_detection(min_scores=0.4, iou_thres=0.5)
    obj_det.select_model(model_name="yolo_v6", version="accurate")
    return obj_det

@torch.no_grad()
def track(obj_det, frame_name="frame"):
    obj_track = Tracking()
    obj_track.config_tracking(max_movement=1000, min_confidence_obj=5, min_out_of_frame=20)
    fps_calculator = CalcFPS()
    video = LoadVideo("/home/mew/Desktop/Object_tracking/video/walking.avi")
    
    for frame in video:
        fps_calculator.start_time()
        obj_track.reset_temp_data()
        result = obj_det.detect(frame)
        obj_track.give_object(result)
        obj_track.tracking_process()
        fps = fps_calculator.calculate()
        
        obj_track.draw_frame(frame, fps)
        video.show_video(frame_name)
        video.wait_key()

    print("count :", obj_track.get_amount_object())
    
if __name__ == "__main__":
    det = model()
    mp.set_start_method('spawn')
    processes = []
    p1 = mp.Process(target=track, args=(det, "frame1",))
    p2 = mp.Process(target=track, args=(det, "frame2",))
    processes.append(p1)
    processes.append(p2)
    p1.start()
    p2.start()
    for p in processes:
        p.join()