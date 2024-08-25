from pathlib import Path
import os

DEVICE_ID = 1

POST_URL = {
    'camera' : 'https://service.novacamera.online/camera',
    'frame' : 'https://service.novacamera.online/frame',
}

VIDEO_ROOT = Path(os.path.abspath(__file__)).parents[0] / Path("temp")
VIDEO_TAIL = VIDEO_ROOT / Path("tail")
VIDEO_CURRENT = VIDEO_ROOT / Path("current")
VIDEO_ALL = VIDEO_ROOT.parents[1] / Path("Video")

for folder in [VIDEO_ROOT, VIDEO_TAIL, VIDEO_CURRENT, VIDEO_ALL]:
    if not os.path.exists(folder):
        os.makedirs(folder)

TRACKER = 'bytetrack.yaml'

EXT_VIDEO = ".avi"
N_PREVIOUS_FRAME = 10

# WIDTH = 768
# HEIGHT = 576

WIDTH = 800
HEIGHT = 600

video_length_time = 60 # in second

FPS = 10

REDIS_CLIENT = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}