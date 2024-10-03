from pathlib import Path
import os

class Config:

    DEVICE_ID = 'cam1'

    POST_URL = {
        'camera' : 'https://service.novacamera.online/camera',
        'frame' : 'https://service.novacamera.online/frame',
    }

    ROOT = Path(os.path.abspath(__file__)).parents[1]
    VIDEO_ROOT = ROOT / Path("temp")
    VIDEO_TAIL = VIDEO_ROOT / Path("tail")
    VIDEO_CURRENT = VIDEO_ROOT / Path("current")
    VIDEO_ALL = VIDEO_ROOT.parents[2] / Path("Video")

    for folder in [VIDEO_ROOT, VIDEO_TAIL, VIDEO_CURRENT, VIDEO_ALL]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    TRACKER = ROOT / 'weights' / 'bytetrack.yaml'
    MODEL_PATH = ROOT / 'weights' / 'yolov8n.pt'

    EXT_VIDEO = ".avi"
    N_PREVIOUS_FRAME = 10

    video_length_time = 60 # in second
    offset_time = 3 # in second

    FPS = 10

    REDIS_CLIENT = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "decode_responses": True
    }