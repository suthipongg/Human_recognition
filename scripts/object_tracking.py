from pathlib import Path
import sys, logging, os, re

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.manage_media import LoadVideo
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
        for n, cls in enumerate(ls_cls):
            if cls in [1, 2, 3, 5, 7] and data['max_id']['car'] < track_id[n]:
                data['max_id']['car'] = track_id[n]
                if count: 
                    data['count']['car'] += 1
            elif cls == 0 and data['max_id']['person'] < track_id[n]:
                data['max_id']['person'] = track_id[n]
                if count: 
                    data['count']['person'] += 1

def tracking_process(process_id, file, model_path='yolov8n.pt'):
    logging.info(f"process {process_id} computing {file}")
    video_processs_path = ROOT / Config.VIDEO_PROCESS_FOLDER / str(process_id) / file
    previous_video_path = ROOT / Config.VIDEO_PREVIOUS / ('0_'+ ext_file_name(file)[1] + Config.EXT_VIDEO)
    meta_data = {'car':0, 'person':0}
    data = {'count': meta_data.copy(), 'max_id': meta_data.copy()}

    model = load_model(model_path)
    if os.path.exists(previous_video_path):
        video = LoadVideo(previous_video_path)
        get_track_data(video, model, data)
                    
        video.add_video(video_processs_path)
    else:
        video = LoadVideo(video_processs_path)
    get_track_data(video, model, data, count=True)
    
    time = int(ext_file_name(file)[0])
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