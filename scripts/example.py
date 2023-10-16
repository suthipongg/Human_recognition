from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    
from scripts.object_tracking import Tracking
from scripts.object_detection import ObjectDetection
from scripts.calculator import CalcFPS
from scripts.manage_media import LoadVideo, manage_queue
import Config
import threading

import torch
import torch.multiprocessing as mp

from time import time

@torch.no_grad()
def model():
    obj_det = ObjectDetection()
    obj_det.config_model_detection(min_scores=0.4, iou_thres=0.5)
    obj_det.select_model(model_name="yolo_v6", version="accurate")
    return obj_det

@torch.no_grad()
def track(obj_det, porcess_id=0, shared_device_queue=None, shared_device_free_process=None):
    obj_track = Tracking()
    obj_track.config_tracking(max_movement=1000, min_confidence_obj=5, min_out_of_frame=20)
    fps_calculator = CalcFPS()
    st = time()
    while 1:
        if time() - st > 5:
            print("======= process", porcess_id, "=======")
            print("shared_device_queue : ", shared_device_queue[porcess_id])
            print("shared_device_free_process : ", shared_device_free_process[porcess_id])
            st = time()
        if shared_device_queue[porcess_id] != None and not shared_device_free_process[porcess_id]:
            video = LoadVideo(shared_device_queue[porcess_id]['path'])
            for frame in video:
                fps_calculator.start_time()
                obj_track.reset_temp_data()
                result = obj_det.detect(frame)
                obj_track.give_object(result)
                obj_track.tracking_process()
                fps = fps_calculator.calculate()
                
                obj_track.draw_frame(frame, fps)
                video.show_video("frame"+str(porcess_id))
                video.wait_key()
            
            shared_device_free_process[porcess_id] = True
            print("count :", obj_track.get_amount_object())

def start_queue(mn_q_system):
    mn_q_system.start_queue_system()

if __name__ == "__main__":
    det = model()
    num_processes = Config.N_GPU
    mn_q_system = manage_queue()

    mp.set_start_method('spawn')
    
    manager = mp.Manager()
    shared_device_queue = manager.list(mn_q_system.device_queue)
    shared_device_free_process = manager.list(mn_q_system.device_free_process)
    mn_q_system.set_share_variable(shared_device_queue, shared_device_free_process)
    
    manage_queue_thread = threading.Thread(target=start_queue, args=(mn_q_system,))
    manage_queue_thread.start()
    
    processes = []
    for porcess_id in range(num_processes):
        p = mp.Process(target=track, args=(det, porcess_id, shared_device_queue, shared_device_free_process))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
        
    manage_queue_thread.join()