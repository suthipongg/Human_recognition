from pathlib import Path
import sys, logging, os, re, json
from datetime import datetime
import torch
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.manage_media import LoadVideo
from scripts.post_data import post_camera, post_frame
import Config

from ultralytics import YOLO

import numpy as np
import cv2
from collections import defaultdict
import time
from tqdm import tqdm
track_history = defaultdict(lambda: [])

# extract timestamp and camID from file name (timestamp_camID.ExtName)
def ext_file_name(file):
    temp = os.path.splitext(file)[0]
    return re.split('_', temp) # return [timestamp, camID]

# load model object tracking
def load_model(model_path='yolov8n.pt', core=0):
    device = torch.device(f'cuda:{core}' if torch.cuda.is_available() else 'cpu')
    torch.cuda.set_device(device)
    model = YOLO(model_path)
    return model

def init_write_video(cam_id, current_time):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    file_name = str(ROOT / 'video/result/' / f'{str(time.time())}_result.avi')
    out = cv2.VideoWriter(file_name, fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
    return out

# get tracking data from video
def get_track_data(video, model, data, tracker='bytetrack.yaml', start_count=False, save_result=False):
    # # save result video
    if start_count and save_result:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(ROOT / 'video' / 'result' / f'{str(time.time())}_result.avi'), fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
    
    # tracking object
    for frame in tqdm(video):
        results = model.track(frame, persist=True, tracker=str(ROOT / 'weights' / tracker), classes=[0, 1, 2, 3, 5, 7], verbose=False)
        track_id = results[0].boxes.id
        n_car = n_person = 0
        
        # if no object detected
        if track_id is None:
            continue
        
        # count number of car and person
        for n, cls in enumerate(results[0].boxes.cls):
            # car
            if cls in [1, 2, 3, 5, 7] and data['max_id']['car'] < track_id[n]:
                # update max_id
                data['max_id']['car'] = track_id[n]
                # count number of car and person in frame if count is True
                if start_count: 
                    n_car += 1
                    data['count']['car'] += 1
            # human
            elif cls == 0 and data['max_id']['person'] < track_id[n]:
                data['max_id']['person'] = track_id[n]
                if start_count: 
                    n_person += 1
                    data['count']['person'] += 1
        # update number of car and person in frame when tracking current video
        if start_count:
            data['frame']['car'] = max(data['frame']['car'], n_car)
            data['frame']['person'] = max(data['frame']['person'], n_person)
            if save_result:
                annotated_frame = results[0].plot()
                # Plot the tracks
                for box, track_id in zip(results[0].boxes.xywh.cpu(), track_id.cpu()):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y)))  # x, y center point
                    if len(track) > 30:  # retain 90 tracks for 90 frames
                        track.pop(0)
                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
                    cv2.putText(annotated_frame, f"person {data['count']['person']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(annotated_frame, f"car    {data['count']['car']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                # save img
                out.write(annotated_frame)
    if start_count and save_result:
        out.release()
    
def save_json_data(data, cam_id, file):
    timestamp = int(ext_file_name(file)[0])
    date_time = datetime.fromtimestamp(int(timestamp)).date()
    # load previous data from json file
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'r') as file_json:
        data_json = json.load(file_json)
        file_json.close()
    # update data
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'w') as file_json:
        for key, value in data['count'].items():
            if date_time > datetime.strptime(data_json['date'], "%Y-%m-%d").date():
                data_json['count'][key] = value
            else:
                data_json['object'][key] += value
        # post data to server
        # post_camera(cam_id, data_json['object'], timestamp)
        # post_frame(cam_id, data['frame'], timestamp)
        # save data to json file
        data_json['date'] = str(date_time)
        json.dump(data_json, file_json)
        file_json.close()


def tracking_process(process_id, file, model_path='yolov8n.pt'):
    # initial data
    cam_id = ext_file_name(file)[1]
    video_processs_path = ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id) / file
    previous_video_path = ROOT / Config.VIDEO_PREVIOUS / ('0_'+ cam_id + Config.EXT_VIDEO)
    meta_data = {'car':0, 'person':0}
    data = {'count': meta_data.copy(), 'frame': meta_data.copy(), 'max_id': meta_data.copy()}
    
    logging.info(f"process {process_id} loading model")
    model = load_model(model_path, process_id)
    
    logging.info(f"process {process_id} computing {file}")
    # compute previous frame if exist and add current video
    if os.path.exists(previous_video_path):
        video = LoadVideo(previous_video_path)
        get_track_data(video, model, data, tracker=Config.TRACKER)
        video.add_video(video_processs_path)
    # add current video
    else:
        video = LoadVideo(video_processs_path)
    # compute current video
    get_track_data(video, model, data, tracker=Config.TRACKER, start_count=True)
        
    logging.info(f"process {process_id} save data")
    # save data to json file + post data to server and remove video
    save_json_data(data, cam_id, file)
    video.save_previous_frame()
    os.remove(video_processs_path)
    logging.info(f"process {process_id} done")

# tracking system
def Track(process_id=0, model_path=str(ROOT / 'weights' / 'yolov8n.pt')):
    logging.basicConfig(level = logging.INFO)
    logging.info("Tracking system initial")
    
    while 1:
        # check if there are video in folder
        for file in os.listdir(ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id)):
            # if there are video, start tracking
            if file.endswith(Config.EXT_VIDEO):
                logging.info(f"process {process_id} start tracking")
                tracking_process(process_id, file, model_path)
            
if __name__ == '__main__':
    Track()