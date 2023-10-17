import cv2
from pathlib import Path
from collections import deque
import numpy as np
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
        self.add_video(p)  # new video

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        ret_val, self.frame = self.cap.read()
        while not ret_val or self.stop:
            self.count += 1
            self.__kill_video()
            raise StopIteration
        return self.frame

    def add_video(self, path):
        self.cap = cv2.VideoCapture(path)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def show_video(self, name_frame="Frame"):
        cv2.imshow(name_frame, self.frame)
        
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
    
class manage_queue:
    def __init__(self):
        logging.basicConfig(level = logging.INFO)
        logging.info("manage queue system initial")
        self.video_temp = [] # for temporary video [[timestamp, id_cam], ...]
        self.video_wait = {} # for wait video {id_cam : [timestamp, ...], ...}
        for n in range(Config.N_CAM):
            self.video_wait[n] = deque()
        self.cam_id_in_queue = np.array([0] * Config.N_CAM)
        self.cam_id_in_process = np.array([False] * Config.N_CAM)
        self.device_free_process = [True] * Config.N_GPU
        self.device_queue = [None] * Config.N_GPU
        
        self.__check_directory_created(Config.VIDEO_TEMP_FOLDER)
        self.__check_directory_created(Config.VIDEO_PROCESS_FOLDER)
        for file in os.listdir(Path(ROOT / Config.VIDEO_PROCESS_FOLDER)):
            Path(ROOT / Config.VIDEO_PROCESS_FOLDER / file).rename(Path(ROOT / Config.VIDEO_TEMP_FOLDER / file))
    
    def set_share_variable(self, share_device_queue, share_device_free_process):
        self.device_queue = share_device_queue
        self.device_free_process = share_device_free_process
    
    def __check_directory_created(self, name):
        if str(name) not in os.listdir(ROOT):
            os.mkdir(Path(ROOT / name)) 
    
    def scan_directory(self):
        self.video_temp = os.listdir(Path(ROOT / Config.VIDEO_TEMP_FOLDER))
        self.video_temp.sort()
    
    def __move_file(self, file):
        src_file = Path(ROOT / Config.VIDEO_TEMP_FOLDER / file)
        if file not in os.listdir(Path(ROOT / Config.VIDEO_PROCESS_FOLDER)):
            dst_file = Path(ROOT / Config.VIDEO_PROCESS_FOLDER / file)
            src_file.rename(dst_file)
            return True
        else:
            os.remove(src_file)
            return False
        
    def __add_id_cam(self, id_cam):
        self.cam_id_in_queue[id_cam] += 1
    
    def extract_add_name(self):
        for file in self.video_temp:
            temp_file = os.path.splitext(file)[0]
            temp_file = re.split('_', temp_file)
            id_cam = int(temp_file[1])
            self.video_wait[id_cam].append(int(temp_file[0]))
            if self.__move_file(file):
                self.__add_id_cam(id_cam)
    
    def get_queue_process(self):
        return np.where(list(self.device_free_process))[0]
    
    def __delete_succes_video(self, process_id):
        os.remove(self.device_queue[process_id]['path'])
        
    def check_success_video(self, process_id):
        if self.device_free_process[process_id] == True and self.device_queue[process_id] != None:
            self.__delete_succes_video(process_id)
            cam_id = self.device_queue[process_id]['cam_id']
            self.cam_id_in_process[cam_id] = False
            self.device_queue[process_id] = None
            
    def __cam_in_queue_and_free_process(self):
        return self.cam_id_in_queue * (self.cam_id_in_process == False)
            
    def have_cam_queue_in_free_process(self):
        return max(self.__cam_in_queue_and_free_process()) != 0
    
    def get_queue_cam(self):
        return np.argmax(self.__cam_in_queue_and_free_process())
    
    def __fullpath(self, file, cam_id):
        filename = str(file) + "_" + str(cam_id) + Config.EXT_VIDEO
        return Path(ROOT / Config.VIDEO_PROCESS_FOLDER / filename)
    
    def set_video_process(self, process_id, cam_id):
        self.cam_id_in_process[cam_id] = True
        file = self.video_wait[cam_id].popleft()
        self.cam_id_in_queue[cam_id] -= 1
        self.device_queue[process_id] = {'path':self.__fullpath(file, cam_id), 'cam_id':cam_id}
        self.device_free_process[process_id] = False
    
    def set_process_success(self, process_id):
        self.device_free_process[process_id] = True
    
    def start_queue_system(self):
        logging.info("manage queue system started")
        while 1:
            self.scan_directory()
            self.extract_add_name()
            
            for process_id in self.get_queue_process():
                self.check_success_video(process_id)
                if self.have_cam_queue_in_free_process():
                    cam_id = self.get_queue_cam()
                    self.set_video_process(process_id, cam_id)
        logging.info("manage queue system exit")

if __name__ == "__main__":
    mn = manage_queue()
    mn.start_queue_system()