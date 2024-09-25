from pathlib import Path

class Config:
    DEVICE_ID = "cam1"

    VIDEO_TEMP = Path(__file__).parents[1] / Path("temp")
    VIDEO_ALL = VIDEO_TEMP.parents[1] / Path("Video")
    
    EXT_VIDEO = ".avi"
    VIDEO_LENGTH_TIME = 10
    FPS = 10

    REDIS_CLIENT = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "decode_responses": True
    }