import os, sys, logging, time
from pathlib import Path
import Config
from scripts.manage_media import scan_video
from scripts.object_tracking import tracking_process
from scripts.post_data import post_camera, post_frame
from scripts.redis_controller import check_redis_connection, clear_redis_data, set_redis_data, get_redis_data
from datetime import datetime

if not check_redis_connection:
    exit()

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

logging.basicConfig(level = logging.INFO)
logging.info("object tracking")

def check_video():
    for video in os.listdir(Config.VIDEO_CURRENT):
        if video.endswith(Config.EXT_VIDEO):
            current_video = Config.VIDEO_CURRENT / video
            break
        os.remove(Config.VIDEO_CURRENT / video)
    else:
        current_video = scan_video()
    return current_video

def process_data(id, data):
    data_previous = get_redis_data(id)
    date_time = datetime.fromtimestamp(int(timestamp)).date()

    if data_previous is None:
        data_previous = data['count'].copy()
        data_previous['date'] = date_time.strftime("%Y-%m-%d")
        set_redis_data(id, data_previous)
        return data
    
    # update data
    for key, value in data['count'].items():
        if date_time > datetime.strptime(data_previous['date'], "%Y-%m-%d").date():
            data_previous[key] = value
        else:
            data_previous[key] += value
    
    # save data
    data_previous['date'] = date_time.strftime("%Y-%m-%d")
    set_redis_data(id, data_previous)
    data_previous.pop('date')
    data['count'] = data_previous
    return data

while True:
    current_video = check_video()
    if current_video is None:
        logging.info("no video found")
        time.sleep(5)
        continue

    logging.info("start tracking")
    timestamp = int(current_video.stem)
    data_info = tracking_process(current_video)
    data_info['timestamp'] = timestamp
    data_info = process_data('previous_data', data_info)

    time_device = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    post_camera(data_info['count'], time_device)
    post_frame(data_info['frame'], time_device)

    logging.info("end tracking")