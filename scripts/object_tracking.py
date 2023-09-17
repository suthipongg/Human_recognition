from pathlib import Path
import sys

script = Path(__file__).resolve().parent
if str(script) not in sys.path:
    sys.path.append(str(script))

from draw import Draw_image, Color
from object_detection import ObjectDetection
from collections import deque
import numpy as np
import time
import cv2
import math

class Tracking:
    def __init__(self):
        '''
        center_points_cur_frame = "object that detected in current frame"
        center_points_cur_frame_remain = "object that detected in current frame but not yet tracking"
        tracking_objects = "object that detected in current frame" or "tracked but checking out of frame"
        '''
        self.center_points_cur_frame = [] # [contain class_obj, (point x,y,wper2,hper2)]
        self.center_points_cur_frame_remain = []
        self.tracking_objects = {} # contain object_id : [class_obj, (point x,y,wper2,hper2), confident, out_of_frame]
        self.track_id = 0
        self.frame = None
        self.count_person = 0
        self.firt_tracking = True
        
        self.cur_old_conf_detected = [] # "for draw image"
        self.cur_old_not_conf_detected = [] # "for draw image"
        self.tracking_out_objects = [] # "for draw image"

    def select_model_detection(self, model_name, version):
        self.model = ObjectDetection()
        self.model.select_model(model_name, version)
        
    def config_model_detection(self, min_scores=0.7, iou_thres=0.5, max_det=1000):
        self.iou_thres = iou_thres
        self.min_scores = min_scores
        self.max_det = max_det

    def config_tracking(self, max_movement=20, min_confidence_obj=2, min_out_of_frame=2):
        self.max_movement = max_movement
        self.min_confidence_obj = max(0, min_confidence_obj-1)
        self.min_out_of_frame = max(0, min_out_of_frame-1)

    def open_video(self, video):
        self.cap = cv2.VideoCapture(video)

    def get_amount_person(self):
        return self.count_person

    def reset_data(self):
        self.cur_old_conf_detected = [] # "for draw image"
        self.cur_old_not_conf_detected = [] # "for draw image"
        self.tracking_out_objects = [] # "for draw image"
        
        self.center_points_cur_frame = []

    def __start_loop(self):
        self.reset_data()
        ret, self.frame = self.cap.read()
        return ret

    def __kill_process(self):
        return cv2.waitKey(1) == 27
    
    def __detect_object(self):
        self.center_points_cur_frame = self.model.detect(self.frame, self.min_scores, self.iou_thres, self.max_det)

    def __update_position(self, class_obj, pt_tracked):
        min_dist = self.max_movement
        object_exists = False
        pt_min_dist = None
        for class_obj_search, pt in self.center_points_cur_frame_remain:
            distance = math.hypot(pt_tracked[0] - pt[0], pt_tracked[1] - pt[1])
            if distance < min_dist and class_obj == class_obj_search:
                min_dist = distance
                pt_min_dist = pt
                object_exists = True
        return pt_min_dist, object_exists

    def __out_of_frame(self, out_of_frame, object_id):
        if out_of_frame >= self.min_out_of_frame:
            self.tracking_objects.pop(object_id)
        else: 
            self.tracking_objects[object_id][3] += 1 # out_of_frame
            
            self.tracking_out_objects.append(self.tracking_objects[object_id][0:2]) # "for draw image"

    def __confident_in_frame(self, confident, object_id, pt_min_dist):
        self.tracking_objects[object_id][1] = pt_min_dist # point 
        self.center_points_cur_frame_remain.remove(self.tracking_objects[object_id][0:2])
        self.tracking_objects[object_id][3] = 0 # out_of_frame
        if confident < self.min_confidence_obj:
            self.tracking_objects[object_id][2] += 1 # confident
            
            self.cur_old_not_conf_detected.append(self.tracking_objects[object_id][0:2]) # "for draw image"
            
        elif confident == self.min_confidence_obj:
            self.count_person += 1
            self.tracking_objects[object_id][2] += 1 # confident
            
            self.cur_old_conf_detected.append(self.tracking_objects[object_id][0:2]) # "for draw image"
        else:
            self.cur_old_conf_detected.append(self.tracking_objects[object_id][0:2]) # "for draw image"

    def __search_old_ID(self):
        self.center_points_cur_frame_remain = self.center_points_cur_frame.copy()
        for object_id, obj_info in list(self.tracking_objects.items()):
            pt_min_dist, object_exists = self.__update_position(obj_info[0], obj_info[1])
            if object_exists:
                self.__confident_in_frame(obj_info[2], object_id, pt_min_dist)
            else:
                self.__out_of_frame(obj_info[3], object_id)

    def __add_new_ID(self):
        for pt_obj in self.center_points_cur_frame_remain:
            self.tracking_objects[self.track_id] = pt_obj + [0, 0]
            self.track_id += 1

    def detect_and_tracking(self):
        self.__detect_object()
        self.__search_old_ID()
        self.__add_new_ID()

    def __draw_all(self, data, size=5, color=Color.RED, thick=1):
        for class_obj, pt in data:
            x, y, w, h = pt
            Draw_image.draw_all(frame=self.frame, center_point=(x, y), corner_point=((x-w, y-h), (x+w, y+h)),
                                class_obj=class_obj, size=size, color=color, thick=thick)

    def __put_text_image(self, avg_fps, name_frame="Frame"):
        self.__draw_all(self.cur_old_conf_detected, size=6, color=Color.GREEN, thick=2)
        self.__draw_all(self.center_points_cur_frame_remain, size=5, color=Color.RED, thick=1)
        self.__draw_all(self.cur_old_not_conf_detected, size=5, color=Color.RED, thick=1)
        for _, pt in self.tracking_out_objects:
            x, y, _, _ = pt
            draw_color = Color.YELLOW
            Draw_image.draw_point(frame=self.frame, point=(x, y), size=4, color=draw_color)
        offset = 5
        y_offset = Draw_image.draw_text(frame=self.frame, text="Count : " + str(self.count_person), 
                                        point=[offset, offset], color=Color.BLACK)
        Draw_image.draw_text(frame=self.frame, text="FPS : " + str(avg_fps), 
                             point=[offset, offset*2+y_offset], color=Color.BLACK)
        cv2.imshow(name_frame, self.frame)

    def fps_calculate(self):
        if self.firt_tracking:
            self.firt_tracking = False
            self.fps_calculator = CalcFPS()
        else:
            self.__put_text_image(self.fps_calculator.calculate())
        if self.__kill_process():
            cv2.destroyAllWindows()
            return True
        self.fps_calculator.start_time()
        return False

    def start_track(self, view_image=False):
        while 1:
            if not self.__start_loop():
                break
            self.detect_and_tracking()

            if view_image and self.fps_calculate():
                break
            
        self.cap.release()
        return self.get_amount_person()
    
class CalcFPS:
    def __init__(self, nsamples: int = 50):
        self.framerate = deque(maxlen=nsamples)

    def start_time(self):
        self.start = time.time()

    def update(self, duration: float):
        self.framerate.append(duration)

    def accumulate(self):
        if len(self.framerate) > 1:
            return int(np.average(self.framerate))
        else:
            return 0
        
    def calculate(self):
        self.update(1.0 / (time.time() - self.start))
        return self.accumulate()