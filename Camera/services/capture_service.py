import logging, time, sys, os
from pathlib import Path
import cv2
import base64

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from services.redis_service import RedisClient
from modules.camera_module import CameraModule
from Configs.config import Config



class VideoManager:
    cam_info = {"timestamp":0, "save":False, "video":None, "frame":None, "realtime":False}
    spin_recoed = True
    start_time_record = time.time()
    video_obj = None


class CaptureService:
    def __init__(self):
        self.width = self.height = 0

    # video_name = timestamp_camID.ExtName
    def name_video(self, current_time):
        return str(round(current_time)) + Config.EXT_VIDEO
    
    # create video file
    def create_video(self,current_time):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        file_name = self.name_video(current_time)
        out = cv2.VideoWriter(
            str(Config.VIDEO_TEMP / file_name), 
            fourcc, 
            Config.FPS, 
            (self.width, self.height)
            )
        logging.info(f"create video file: {file_name}")
        return out

    # move video file when finish recording
    def move_file(self,file):
        src_file = Path(Config.VIDEO_TEMP / file)
        dst_file = Path(Config.VIDEO_ALL / file)
        src_file.rename(dst_file)
        logging.info(f"move video file: {file}")

    # receive video and save to video file for each camera id
    def write_video(self,frame, timestamp):
        if RedisClient.get_redis_data('stream').get('status', False):
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frame = base64.b64encode(buffer).decode("utf-8")
            RedisClient.set_redis_data('frame', {'frame':base64_frame})
        # if not start record video, create new video file
        if VideoManager.spin_recoed:
            VideoManager.start_time_record = timestamp
            VideoManager.spin_recoed = False
            VideoManager.video_obj = self.create_video(VideoManager.start_time_record)

        VideoManager.video_obj.write(frame)
        
        # check if video length time is reached, release video file
        if timestamp - VideoManager.start_time_record > Config.VIDEO_LENGTH_TIME:
            VideoManager.spin_recoed = True
            VideoManager.video_obj.release()
            self.move_file(self.name_video(VideoManager.start_time_record))

    def remove_old_file(self):
        for file in os.listdir(Config.VIDEO_TEMP):
            os.remove(Config.VIDEO_TEMP / file)


    def run_camera(self):
        try:
            self.remove_old_file()
            cam = CameraModule()
            self.width = int(cam.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cam.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            while (cam.camera_is_opened()):
                try:
                    frame = cam.read_camera()
                    if frame is not None:
                        self.write_video(frame, time.time())
                    else:
                        logging.error("Error reading frame")
                        # break
                except Exception as e:
                    logging.error(f"Error receiving image: {e}")
                    raise e
            logging.info(f"camera stopped reading")
        except Exception as e:
            logging.error(str(e))
            raise e

if __name__ == "__main__":
    RedisClient.connecct()
    camera = CaptureService()
    camera.run_camera()