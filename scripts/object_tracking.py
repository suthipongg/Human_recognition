from pathlib import Path
import sys, logging, os, re, json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.manage_media import LoadVideo
from scripts.post_data import post_camera, post_frame
import Config

from ultralytics import YOLO

def ext_file_name(file):
    temp = os.path.splitext(file)[0]
    return re.split('_', temp)

def load_model(model_path='yolov8n.pt'):
    return YOLO(model_path)

def get_track_data(video, model, data, count=False):
    for frame in video:
        results = model.track(frame, persist=True, tracker=str(ROOT / 'weights' / 'bytetrack.yaml'), classes=[0, 1, 2, 3, 5, 7])
        track_id = results[0].boxes.id
        ls_cls = results[0].boxes.cls
        n_car = n_person = 0
        if track_id is None:
            continue

        for n, cls in enumerate(ls_cls):
            if cls in [1, 2, 3, 5, 7]:
                n_car += 1
                if data['max_id']['car'] < track_id[n]:
                    data['max_id']['car'] = track_id[n]
                    if count: 
                        data['count']['car'] += 1
            elif cls == 0:
                n_person += 1
                if data['max_id']['person'] < track_id[n]:
                    data['max_id']['person'] = track_id[n]
                    if count: 
                        data['count']['person'] += 1
        if count:
            data['frame']['car'] = max(data['frame']['car'], n_car)
            data['frame']['person'] = max(data['frame']['person'], n_person)

def save_json_data(data, cam_id, file):
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'r') as file_json:
        data_json = json.load(file_json)
        file_json.close()
        
    timestamp = int(ext_file_name(file)[0])
    with open(ROOT / Config.DATA_TRACKING_FOLDER / (cam_id+'.json'), 'w') as file_json:
        for key, value in data['count'].items():
            data['count'][key] = value + data_json[key]
        json.dump(data['count'], file_json)
        post_camera(cam_id, data['count'], timestamp)
        post_frame(cam_id, data['frame'], timestamp)
        file_json.close()

def tracking_process(process_id, file, model_path='yolov8n.pt'):
    logging.info(f"process {process_id} computing {file}")
    cam_id = ext_file_name(file)[1]
    video_processs_path = ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id) / file
    previous_video_path = ROOT / Config.VIDEO_PREVIOUS / ('0_'+ cam_id + Config.EXT_VIDEO)
    meta_data = {'car':0, 'person':0}
    data = {'count': meta_data.copy(), 'frame': meta_data.copy(), 'max_id': meta_data.copy()}

    model = load_model(model_path)
    if os.path.exists(previous_video_path):
        video = LoadVideo(previous_video_path)
        get_track_data(video, model, data)
                    
        video.add_video(video_processs_path)
    else:
        video = LoadVideo(video_processs_path)
    get_track_data(video, model, data, count=True)
    
    save_json_data(data, cam_id, file)
        
    video.save_previous_frame()
    os.remove(video_processs_path)

def Track(model_path=str(ROOT / 'weights' / 'yolov8n.pt'), process_id=0):
    logging.basicConfig(level = logging.INFO)
    logging.info("Tracking system initial")
    has_video = False
    
    while 1:
        for file in os.listdir(ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id)):
            if file.endswith(Config.EXT_VIDEO):
                has_video = True
                break
        
        if has_video:
            tracking_process(process_id, file, model_path)
            has_video = False
            
if __name__ == '__main__':
    Track()