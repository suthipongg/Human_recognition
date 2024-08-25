from pathlib import Path
import sys, logging, os

import torch
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.manage_media import LoadVideo
import Config

from ultralytics import YOLO

import numpy as np
import cv2
from collections import defaultdict
import time

# load model object tracking
def load_model(model_path='yolov8n.pt'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.cuda.set_device(device)
    model = YOLO(model_path)
    return model

# get tracking data from video
def get_track_data(video, model, data, tracker='bytetrack.yaml', start_count=False, save_result=False):
    # save result video
    if start_count and save_result:
        track_history = defaultdict(lambda: [])
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if not os.path.exists(ROOT / 'result'):
            os.makedirs(ROOT / 'result')
        out = cv2.VideoWriter(str(ROOT / 'result' / f'{str(time.time())}_result.avi'), fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
    
    # tracking object
    # for frame in tqdm(video):
    for frame in video:
        results = model.track(frame, persist=True, tracker=str(ROOT / 'weights' / tracker), classes=[0, 1, 2, 3, 5, 7], verbose=save_result and start_count)
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


def tracking_process(video_path, model_path='yolov8n.pt'):
    # initial data
    previous_video_path = Config.VIDEO_TAIL / ('tail' + Config.EXT_VIDEO)
    meta_data = {'car':0, 'person':0}
    data = {'count': meta_data.copy(), 'frame': meta_data.copy(), 'max_id': meta_data.copy()}
    
    logging.info(f"loading model")
    model = load_model(model_path)
    
    logging.info(f"computing {video_path}")
    # compute previous frame if exist and add current video
    if os.path.exists(previous_video_path):
        video = LoadVideo(previous_video_path)
        get_track_data(video, model, data, tracker=Config.TRACKER)
        video.add_video(video_path)
    # add current video
    else:
        video = LoadVideo(video_path)
    # compute current video
    get_track_data(video, model, data, tracker=Config.TRACKER, start_count=True)
    video.save_previous_frame('tail')
    os.remove(video_path)
    logging.info(f"done")

    return data