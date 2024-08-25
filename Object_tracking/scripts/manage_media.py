import cv2
from pathlib import Path
from collections import deque
import os, re, sys
import logging

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import Config

class Color():
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    BLACK = (0, 0, 0)
    
class DrawImage():
    @staticmethod
    def draw_point(frame, point, size=5, color=Color.RED):
        cv2.circle(frame, point, size, color, -1)
    
    @staticmethod
    def draw_box(frame, point_L, point_R, color=Color.RED, thick=2):
        cv2.rectangle(frame, point_L, point_R, color, thick)

    @staticmethod
    def draw_text(frame, text, point, color=Color.BLACK):
        lw = max(round(sum(frame.shape) / 2 * 0.003), 2)
        tf = max(lw - 1, 2)  # font thickness
        font_size = lw / 3
        cvt_color = lambda x : abs(x-255)
        x, y = point
        h = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_size, thickness=tf)[0][1]
        new_y = int(y + h + font_size - 1)
        cv2.putText(img=frame, text=text, org=(x, new_y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale=font_size, color=tuple(map(cvt_color, color)), thickness=tf+5)
        cv2.putText(img=frame, text=text, org=(x, new_y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale=font_size, color=color, thickness=tf)
        return new_y
    
    @staticmethod
    def draw_class(frame, point_L, point_R, class_obj, color=Color.RED):
        lw = max(round(sum(frame.shape) / 2 * 0.003), 2)
        tf = max(lw - 1, 2)  # font thickness
        font_size = lw / 4
        w, h = cv2.getTextSize(text=class_obj, fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                               fontScale=font_size, thickness=tf)[0]  # text width, height
        outside = point_L[1] - h - 3 >= 0  # label fits outside box
        point_R = point_L[0] + w, point_L[1] - h - 3 if outside else point_L[1] + h + 3
        cv2.rectangle(frame, point_L, point_R, color, -1, cv2.LINE_AA)  # filled
        cvt_color = lambda x : abs(x-255)
        cv2.putText(img=frame, text=class_obj, org=(point_L[0], point_L[1] - 2 if outside else point_L[1] + h + 2), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_size, color=tuple(map(cvt_color, color)), 
                    thickness=tf)
    
    @staticmethod
    def single_draw_all(frame, center_point, corner_point, class_obj, size=5, color=Color.RED, thick=2):
        DrawImage.draw_point(frame=frame, point=center_point, size=size, color=color)
        DrawImage.draw_box(frame=frame, point_L=corner_point[0], 
                            point_R=corner_point[1], color=color, thick=thick)
        DrawImage.draw_class(frame=frame, point_L=corner_point[0],
                                point_R=corner_point[1], class_obj=class_obj, color=color)
    
    @staticmethod
    def multi_draw_all(frame, data, size=5, color=Color.RED, thick=1):
        for info in data:
            x, y, w, h = info["point"]
            DrawImage.single_draw_all(frame=frame, center_point=(x, y), corner_point=((x-w, y-h), (x+w, y+h)),
                                class_obj=info["class_obj"], size=size, color=color, thick=thick)
            
class LoadVideo:
    def __init__(self, path):
        self.stop = False
        p = str(Path(path).resolve())
        self.id_cam = re.split('_', os.path.splitext(os.path.basename(p))[0])[1]
        self.add_video(p)  # new video
        
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
    
    def show_video(self, name_frame="Frame"):
        cv2.imshow(name_frame, self.frame)
    
    def save_previous_frame(self, file_name, ext=".avi"):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        file_name = file_name + ext
        file_path = str(Config.VIDEO_TAIL / file_name)
        out = cv2.VideoWriter(file_path, fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
        for frame in self.merge_frame:
            out.write(frame)
        out.release()
        self.merge_frame = deque([], maxlen=Config.N_PREVIOUS_FRAME)
    
    def wait_key(self):
        key = cv2.waitKey(1)
        if key == 27:
            self.__kill_video()
        
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
        logging.info("no video found")
        return False