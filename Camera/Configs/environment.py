from pathlib import Path
import os

VIDEO_TEMP = Path(os.path.abspath(__file__)).parents[1] / Path("temp")
VIDEO_ALL = VIDEO_TEMP.parents[1] / Path("Video")

EXT_VIDEO = ".avi"
WIDTH = 800
HEIGHT = 600

DEVICE_ID = 1

VIDEO_LENGTH_TIME = 60

FPS = 10

REDIS_CLIENT = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}