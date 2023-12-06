from pathlib import Path

VIDEO_ROOT = Path("video_root")
UPLOAD_FOLDER = VIDEO_ROOT / Path("video_uploads")
VIDEO_TEMP_FOLDER = VIDEO_ROOT / Path("video_temp")
VIDEO_PROCESS_FOLDER = VIDEO_ROOT / Path("video_process")
VIDEO_PREVIOUS = VIDEO_ROOT / Path("video_previous")
DATA_TRACKING_FOLDER = VIDEO_ROOT / Path("data_tracking")

N_GPU = 2
N_CAM = 2

EXT_VIDEO = ".avi"
N_PREVIOUS_FRAME = 10

WIDTH = 768
HEIGHT = 576

# WIDTH = 800
# HEIGHT = 600

video_length_time = 10 # in second

FPS = 10

IP_CONVERTER = {
    "172.20.10.3" : 0,
    "172.20.10.2" : 1,
}