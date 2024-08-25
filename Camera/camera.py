import os, sys, logging, time
import Configs.environment as config
from pathlib import Path
import numpy as np
import cv2
from scripts.redis_controller import check_redis_connection, get_redis_data, set_redis_data, clear_redis_data

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

logging.basicconfig(level = logging.INFO)
logging.info("create video service initial")

for file in os.listdir(config.VIDEO_TEMP):
    os.remove(config.VIDEO_TEMP / file)

cam_info = {"timestamp":0, "save":False, "video":None, "frame":None, "realtime":False}

spin_recoed = True
start_time_record = time.time()
video_obj = None

# video_name = timestamp_camID.ExtName
def name_video(current_time):
    return str(current_time) + config.EXT_VIDEO

# create video file
def create_video(current_time):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    file_name = name_video(round(current_time))
    out = cv2.VideoWriter(str(ROOT / config.VIDEO_TEMP / file_name), fourcc, config.FPS, (config.WIDTH, config.HEIGHT))
    return out

# decode image data from espcam
def preprocess(img):
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img

# move video file when finish recording
def move_file(file):
    src_file = Path(ROOT / config.VIDEO_TEMP / file)
    dst_file = Path(ROOT / config.VIDEO_ALL / file)
    src_file.rename(dst_file)

# receive video and save to video file for each camera id
def receive_video(frame, timestamp):
    img = preprocess(frame)
    if get_redis_data('stream').get('status'):
        set_redis_data(config.DEVICE_ID, img)
    # if not start record video, create new video file
    if spin_recoed:
        start_time_record = timestamp
        spin_recoed = False
        video_obj = create_video(start_time_record)

    video_obj.write(img)
    
    # check if video length time is reached, release video file
    if timestamp - start_time_record > config.VIDEO_LENGTH_TIME:
        spin_recoed = True
        video_obj.release()
        move_file(name_video(start_time_record))
    return start_time_record

def read_camera():
    return

if __name__ == "__main__":
    try:
        # camera connection
        cam = None
        # while connection is open
        while (cam):
            try:
                if (time.time() - start_time_record) * config.FPS >= 1:
                    # Receive image data from ESP32-CAM
                    frame = read_camera()
                    if frame:
                        start_time_record = receive_video(frame)
            except Exception as e:
                print(f"Error receiving image: {e}")
                raise e
        print(f"camera stopped reading")
    except Exception as e:
        print(str(e))