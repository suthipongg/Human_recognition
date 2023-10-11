from pathlib import Path

UPLOAD_FOLDER = Path("video_uploads")
VIDEO_TEMP_FOLDER = Path("video_temp")
VIDEO_PROCESS_FOLDER = Path("video_process")

N_GPU = 2
N_CAM = 2

EXT_VIDEO = ".mp4"

WIDTH = 800
HEIGHT = 600

video_length_time = 10 # in second

FPS = 10

IP_CONVERTER = {
    "172.20.10.3" : 0,
    "172.20.10.2" : 1,
}