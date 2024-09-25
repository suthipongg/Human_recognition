import cv2
from pathlib import Path
from collections import deque
import os, re, sys
import logging

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from Configs.config import Config
            
class LoadVideo:
    def __init__(self, path):
        self.stop = False
        p = str(Path(path).resolve())
        self.id_cam = re.split('_', os.path.splitext(os.path.basename(p))[0])[1]
        self.add_video(p)
        
        self.merge_frame = deque([], maxlen=Config.N_PREVIOUS_FRAME) 
        self.n_frmae = 0

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        ret_val, self.frame = self.cap.read()
        if self.frames - self.n_frmae <= Config.N_PREVIOUS_FRAME and ret_val:
            self.merge_frame.append(self.frame)
        self.n_frmae += 1
        while not ret_val or self.stop:
            self.count += 1
            self.__kill_video()
            raise StopIteration
        return self.frame

    def add_video(self, path):
        self.stop = False
        self.cap = cv2.VideoCapture(str(path))
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def save_previous_frame(self, file_name):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        file_name = file_name + Config.EXT_VIDEO
        file_path = str(Config.VIDEO_TAIL / file_name)
        out = cv2.VideoWriter(file_path, fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
        for frame in self.merge_frame:
            out.write(frame)
        out.release()
        self.merge_frame = deque([], maxlen=Config.N_PREVIOUS_FRAME)
    
    def __kill_video(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.stop = True

    def __len__(self):
        return self.frames  # amount of frames
    
def scan_video():
    logging.basicConfig(level = logging.INFO)
    logging.info("manage queue system initial")
    
    video_names = os.listdir(Config.VIDEO_ALL)
    video_names.sort()

    for video_name in video_names:
        if video_name.endswith(Config.EXT_VIDEO):
            (Config.VIDEO_ALL / video_name).rename(Config.VIDEO_CURRENT / video_name)
            return Config.VIDEO_CURRENT / video_name
        else:
            os.remove(Config.VIDEO_ALL / video_name)
    logging.info("no video found")
    return False