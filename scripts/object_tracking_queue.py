from pathlib import Path
import sys, logging, os

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    
from scripts.tracking import Tracking
from scripts.object_detection import ObjectDetection
from scripts.calculator import CalcFPS
from scripts.manage_media import LoadVideo, manage_queue
import Config
import threading
import json

import torch
import torch.multiprocessing as mp

@torch.no_grad()
def model(min_scores=0.4, iou_thres=0.5, max_det=1000, model_name="yolo_v6", version="accurate", device="0"):
    obj_det = ObjectDetection()
    obj_det.config_model_detection(min_scores=min_scores, iou_thres=iou_thres, max_det=max_det)
    obj_det.select_model(model_name=model_name, version=version, device=device)
    logging.info(f"model object detection initial")
    return obj_det

def check_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

@torch.no_grad()
def Object_tracking(obj_det, porcess_id=0, shared_device_queue=None, shared_device_free_process=None):
    logging.info(f"Object tracking system process {porcess_id} initial")
    if not shared_device_queue or not shared_device_free_process:
        logging.error("shared_device_queue or shared_device_free_process is None")
        return
    obj_track = Tracking()
    obj_track.config_tracking(max_movement=1000, min_confidence_obj=5, min_out_of_frame=20)
    fps_calculator = CalcFPS()
    
    data_tracking_folder_path = ROOT / Config.DATA_TRACKING_FOLDER
    check_folder(data_tracking_folder_path)
    while 1:
        if shared_device_queue[porcess_id] != None and not shared_device_free_process[porcess_id]:
            logging.info(f"process {porcess_id} computing {shared_device_queue[porcess_id]['path'].stem}")
            cam_id = shared_device_queue[porcess_id]['cam_id']
            json_file = f"{cam_id}.json"
            json_file_path  = data_tracking_folder_path / json_file
            if json_file in os.listdir(ROOT / Config.DATA_TRACKING_FOLDER):
                with open(json_file_path, 'r') as openfile:
                    obj_track.set_data_tracking(json.load(openfile))
                
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
            
            data_tracking = obj_track.get_data_tracking()
            json_object = json.dumps(data_tracking, indent=4)
            with open(json_file_path, "w") as outfile:
                outfile.write(json_object)
                
            obj_track.reset_data_tracking()
            shared_device_free_process[porcess_id] = True
            logging.info(f"process {porcess_id} compute {shared_device_queue[porcess_id]['path'].stem} success")
    logging.info(f"Object tracking system process {porcess_id} end")


def start_queue(mn_q_system):
    mn_q_system.start_queue_system()


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    det = model(device="cpu")
    mn_q_system = manage_queue()

    mp.set_start_method('spawn')
    
    manager = mp.Manager()
    shared_device_queue = manager.list(mn_q_system.device_queue)
    shared_device_free_process = manager.list(mn_q_system.device_free_process)
    mn_q_system.set_share_variable(shared_device_queue, shared_device_free_process)
    
    manage_queue_thread = threading.Thread(target=start_queue, args=(mn_q_system,))
    manage_queue_thread.start()
    
    processes = []
    for porcess_id in range(Config.N_GPU):
        p = mp.Process(target=Object_tracking, args=(det, porcess_id, shared_device_queue, shared_device_free_process))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
        
    manage_queue_thread.join()