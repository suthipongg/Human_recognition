from pathlib import Path

VIDEO_ROOT = Path("video_root")
UPLOAD_FOLDER = VIDEO_ROOT / Path("video_uploads")
VIDEO_TEMP_FOLDER = VIDEO_ROOT / Path("video_temp")
VIDEO_PROCESS_FOLDER = VIDEO_ROOT / Path("video_process")
VIDEO_PREVIOUS = VIDEO_ROOT / Path("video_previous")
DATA_TRACKING_FOLDER = VIDEO_ROOT / Path("data_tracking")

TRACKER = 'bytetrack.yaml'


CHIP_ID = {
    "405a4ce342a8" : 0,
}

N_GPU = 1
N_CAM = len(CHIP_ID)

EXT_VIDEO = ".avi"
N_PREVIOUS_FRAME = 10

# WIDTH = 768
# HEIGHT = 576

WIDTH = 800
HEIGHT = 600

video_length_time = 60 # in second

FPS = 10

POST_URL = {
    'camera' : 'https://service.novacamera.online/camera',
    'frame' : 'https://service.novacamera.online/frame',
}