import os, sys, logging, time
from pathlib import Path
from datetime import datetime, date

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from Configs.config import Config
from modules.manage_media import scan_video
from modules.object_tracking import ObjectTracking
from modules.post_data import post_camera, post_frame
from services.redis_service import RedisClient

logging.basicConfig(level = logging.INFO)
logging.info("object tracking")


class ObjectTrackingService:
    def __init__(self):
        self.object_tracking = ObjectTracking()

    def check_video(self):
        for video in os.listdir(Config.VIDEO_CURRENT):
            if video.endswith(Config.EXT_VIDEO):
                current_video = Config.VIDEO_CURRENT / video
                break
            os.remove(Config.VIDEO_CURRENT / video)
        else:
            current_video = scan_video()
        return current_video

    def process_data(self, id, data):
        data_previous = RedisClient.get_redis_data(id)
        date_time = date.fromtimestamp(int(data['timestamp']))

        if data_previous is None:
            data_previous = data['count'].copy()
            data_previous['date'] = date_time.strftime("%Y-%m-%d")
            RedisClient.set_redis_data(id, data_previous)
            return data
        
        # update data
        for key, value in data['count'].items():
            if date_time > date.strptime(data_previous['date'], "%Y-%m-%d"):
                data_previous[key] = value
            else:
                data_previous[key] += value
        
        # save data
        data_previous['date'] = date_time.strftime("%Y-%m-%d")
        RedisClient.set_redis_data(id, data_previous)
        data_previous.pop('date')
        data['count'] = data_previous
        return data

    def run_tracking(self):
        while True:
            current_video = self.check_video()
            if not current_video:
                logging.info("no video found")
                time.sleep(5)
                continue

            logging.info("start tracking")
            timestamp = int(current_video.stem)
            data_info = self.object_tracking.tracking_process(current_video)
            data_info['timestamp'] = timestamp
            data_info = self.process_data('previous_data', data_info)

            time_device = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            post_camera(data_info['count'], time_device)
            post_frame(data_info['frame'], time_device)

            logging.info("end tracking")