from pathlib import Path

class Config:
    with open("/proc/device-tree/serial-number", "r") as file:
        DEVICE_ID = file.read().replace('\x00', '').strip()

    VIDEO_TEMP = Path(__file__).parents[1] / Path("temp")
    VIDEO_ALL = VIDEO_TEMP.parents[1] / Path("Video")
    
    if not VIDEO_TEMP.exists():
        VIDEO_TEMP.mkdir()
    if not VIDEO_ALL.exists():
        VIDEO_ALL.mkdir()

    EXT_VIDEO = ".avi"
    VIDEO_LENGTH_TIME = 10
    FPS = 10

    REDIS_CLIENT = {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "decode_responses": True
    }