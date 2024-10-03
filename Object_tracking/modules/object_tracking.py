from pathlib import Path
import sys, logging, os

from datetime import date

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from modules.manage_media import LoadVideo
from modules.tracking_model import ObjectTrackingModel
from services.redis_service import RedisClient
from Configs.config import Config


class ObjectTracking:
    def __init__(self, model_path=Config.MODEL_PATH):
        logging.info(f"loading model")
        self.model = ObjectTrackingModel(model_path)
        self.meta_data = {'car':0, 'person':0}
        self.init_data()
        self.first_start = True

    def init_data(self):
        self.data = {'count': self.meta_data.copy(), 'frame': self.meta_data.copy(), 'max_id': self.meta_data.copy()}

    def update_data(self, track_id, class_id, start_count=False):
        n_car = n_person = 0
        for n, cls in enumerate(class_id):
            if cls in self.model.car_id and self.data['max_id']['car'] < track_id[n]:
                self.data['max_id']['car'] = track_id[n]
                if start_count: 
                    n_car += 1
                    self.data['count']['car'] += 1
            elif cls in self.model.human_id and self.data['max_id']['person'] < track_id[n]:
                self.data['max_id']['person'] = track_id[n]
                if start_count: 
                    n_person += 1
                    self.data['count']['person'] += 1
        return n_car, n_person

    def get_track_data(self, video, start_count=False, show_result=False, n_pass_frame=0):
        logging.info("---> get_track_data")
        for frame in video:
            boxes = self.model.track_data(frame, verbose=show_result and start_count)

            if boxes is None:
                logging.info(f"no object detected")
                continue
            track_id, class_id = boxes.id, boxes.cls
            
            n_car, n_person = self.update_data(track_id, class_id, start_count)

            if start_count and n_pass_frame == 0:
                self.data['frame']['car'] = max(self.data['frame']['car'], n_car)
                self.data['frame']['person'] = max(self.data['frame']['person'], n_person)
            elif start_count:
                n_pass_frame -= 1
        logging.info(f"count: {self.data['count']}")


    def tracking_process(self, video_path, show_result=False):
        logging.info(f"---> tracking process")
        self.init_data()
        previous_video = RedisClient.get_redis_data('previous_video')
        difference_time = (int(Path(video_path).stem) - int(previous_video.get('previous_time'))) if previous_video else 0
        video_missing_period = difference_time > (Config.video_length_time + Config.offset_time)
        is_new_day = date.fromtimestamp(int(Path(video_path).stem)) != date.fromtimestamp(int(previous_video.get('previous_time', 0)))

        logging.info(f"computing {video_path}")
        if is_new_day:
            logging.info(f"new day")
            RedisClient.clear_redis_data('previous_video')
            for previous_video in os.listdir(Config.VIDEO_TAIL):
                os.remove(Config.VIDEO_TAIL / previous_video)
                logging.info(f"remove {Config.VIDEO_TAIL / previous_video}")
            video = LoadVideo(video_path)
            self.get_track_data(video, show_result=show_result, start_count=True)
        elif video_missing_period:
            logging.info(f"video missing period")
            self.model.load_model()
            video = LoadVideo(video_path)
            self.get_track_data(video, start_count=True, show_result=show_result, n_pass_frame=Config.N_PREVIOUS_FRAME)
        elif previous_video and self.first_start:
            logging.info(f"previous video")
            previous_video_path = Config.VIDEO_TAIL / ('tail' + Config.EXT_VIDEO)
            video = LoadVideo(previous_video_path)
            self.get_track_data(video, start_count=False)

            video = LoadVideo(video_path)

            self.get_track_data(video, show_result=show_result, start_count=True)
        else:
            logging.info(f"normal")
            video = LoadVideo(video_path)
            self.get_track_data(video, show_result=show_result, start_count=True)

        self.first_start = False

        RedisClient.set_redis_data('previous_video', {'previous_time': Path(video_path).stem}, Config.video_length_time+Config.offset_time)
        video.save_previous_frame('tail')
        os.remove(video_path)
        logging.info(f"remove {video_path}")
        logging.info(f"done")
        return self.data