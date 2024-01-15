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

# file name: timestamp_camID.ExtName
# extract timestamp and camID from file name
def ext_file_name(file):
    temp = os.path.splitext(file)[0]
    # return timestamp, camID
    return re.split('_', temp)

def load_model(model_path='yolov8n.pt', core=0):
    device = torch.device(f'cuda:{core}' if torch.cuda.is_available() else 'cpu')
    model = YOLO(model_path, device=device)
    return model

def get_track_data(video, model, data, tracker='bytetrack.yaml', count=False):
    for frame in video:
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
                if count: 
                    n_car += 1
                    data['count']['car'] += 1
            # human
            elif cls == 0 and data['max_id']['person'] < track_id[n]:
                data['max_id']['person'] = track_id[n]
                if count: 
                    n_person += 1
                    data['count']['person'] += 1
        # update number of car and person in frame
        if count:
            data['frame']['car'] = max(data['frame']['car'], n_car)
            data['frame']['person'] = max(data['frame']['person'], n_person)

def save_json_data(data, cam_id, file):
    timestamp = int(ext_file_name(file)[0])
    date_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    # load previous data from json file
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'r') as file_json:
        data_json = json.load(file_json)
        file_json.close()
    # update data
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'w') as file_json:
        for key, value in data['count'].items():
            if date_time > datetime.strptime(data_json['date'], "%Y-%m-%d"):
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
    else:
        video = LoadVideo(video_processs_path)
    # compute current video
    get_track_data(video, model, data, tracker=Config.TRACKER, count=True)
        
    logging.info(f"process {process_id} save data")
    # save data to json file + post data to server and remove video
    save_json_data(data, cam_id, file)
    video.save_previous_frame()
    os.remove(video_processs_path)
    logging.info(f"process {process_id} done")


def Track(model_path=str(ROOT / 'weights' / 'yolov8n.pt'), process_id=0):
    logging.basicConfig(level = logging.INFO)
    logging.info("Tracking system initial")
    
    while 1:
        # check if there is video in folder
        for file in os.listdir(ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id)):
            # if there is video, start tracking
            if file.endswith(Config.EXT_VIDEO):
                logging.info(f"process {process_id} start tracking")
                tracking_process(process_id, file, model_path)
            
if __name__ == '__main__':
    Track()