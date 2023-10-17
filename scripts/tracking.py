from pathlib import Path
import sys

script = Path(__file__).resolve().parent
if str(script) not in sys.path:
    sys.path.append(str(script))

from scripts.manage_media import DrawImage, Color
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
        self.count_object = {}

    def config_tracking(self, max_movement=20, min_confidence_obj=2, min_out_of_frame=2):
        self.max_movement = max_movement
        self.min_confidence_obj = max(0, min_confidence_obj-1)
        self.min_out_of_frame = max(0, min_out_of_frame-1)

    def get_amount_object(self):
        return self.count_object

    def reset_id_tracking(self):
        temp = {}
        track_id = 0
        for object_id in self.tracking_objects:
            temp[track_id] = self.tracking_objects[object_id]
            track_id += 1
        return temp, track_id
    
    def get_data_tracking(self):
        tracking_objects, track_id = self.reset_id_tracking()
        return {
            "tracking_objects" : tracking_objects,
            "track_id" : track_id,
            "count_object" : self.count_object
        }
        
    def set_data_tracking(self, data):
        self.tracking_objects = data["tracking_objects"]
        self.track_id = data["track_id"]
        self.count_object = data["count_object"]

    def reset_data_tracking(self):
        self.tracking_objects = {}
        self.track_id = 0
        self.count_object = {}

    def reset_temp_data(self):
        self.cur_old_conf_detected = [] # "for draw image"
        self.cur_old_not_conf_detected = [] # "for draw image"
        self.tracking_out_objects = [] # "for draw image"
        
        self.center_points_cur_frame = []
    
    def give_object(self, result):
        self.center_points_cur_frame = result

    def __update_position(self, class_obj, pt_tracked):
        min_dist = self.max_movement
        object_exists = False
        pt_min_dist = None
        for obj_info in self.center_points_cur_frame_remain:
            distance = math.hypot(pt_tracked[0] - obj_info["point"][0], pt_tracked[1] - obj_info["point"][1])
            if distance < min_dist and class_obj == obj_info["class_obj"]:
                min_dist = distance
                pt_min_dist = obj_info["point"]
                object_exists = True
        return pt_min_dist, object_exists

    def __out_of_frame(self, out_of_frame, object_id):
        if out_of_frame >= self.min_out_of_frame or self.tracking_objects[object_id]["conf"] < self.min_confidence_obj:
            self.tracking_objects.pop(object_id)
        else: 
            self.tracking_objects[object_id]["oof"] += 1 # out_of_frame
            
            self.tracking_out_objects.append(self.tracking_objects[object_id]) # "for draw image"

    def __confident_in_frame(self, confident, object_id, pt_min_dist):
        self.tracking_objects[object_id]["point"] = pt_min_dist # point 
        class_obj = self.tracking_objects[object_id]["class_obj"]
        obj_class_pt = self.tracking_objects[object_id].copy()
        obj_class_pt.pop("conf")
        obj_class_pt.pop("oof")
        self.center_points_cur_frame_remain.remove(obj_class_pt)
        self.tracking_objects[object_id]["oof"] = 0 # out_of_frame
        if confident < self.min_confidence_obj:
            self.tracking_objects[object_id]["conf"] += 1 # confident
            
            self.cur_old_not_conf_detected.append(obj_class_pt) # "for draw image"
            
        elif confident == self.min_confidence_obj:
            if class_obj in self.count_object:
                self.count_object[class_obj] += 1
            else:
                self.count_object.setdefault(class_obj, 1)
            self.tracking_objects[object_id]["conf"] += 1 # confident
            
            self.cur_old_conf_detected.append(obj_class_pt) # "for draw image"
        else:
            self.cur_old_conf_detected.append(obj_class_pt) # "for draw image"

    def __search_old_ID(self):
        self.center_points_cur_frame_remain = self.center_points_cur_frame.copy()
        for object_id, obj_info in list(self.tracking_objects.items()):
            pt_min_dist, object_exists = self.__update_position(obj_info["class_obj"], obj_info["point"])
            if object_exists:
                self.__confident_in_frame(obj_info["conf"], object_id, pt_min_dist)
            else:
                self.__out_of_frame(obj_info["oof"], object_id)

    def __add_new_ID(self):
        for obj_info in self.center_points_cur_frame_remain:
            obj_info["conf"] = obj_info["oof"] = 0
            self.tracking_objects[self.track_id] = obj_info
            self.track_id += 1

    def tracking_process(self):
        self.__search_old_ID()
        self.__add_new_ID()

    def draw_frame(self, frame, avg_fps):
        DrawImage.multi_draw_all(frame, self.cur_old_conf_detected, size=6, color=Color.GREEN, thick=2)
        DrawImage.multi_draw_all(frame, self.center_points_cur_frame_remain, size=5, color=Color.RED, thick=1)
        DrawImage.multi_draw_all(frame, self.cur_old_not_conf_detected, size=5, color=Color.RED, thick=1)
        for info in self.tracking_out_objects:
            x, y, _, _ = info["point"]
            draw_color = Color.YELLOW
            DrawImage.draw_point(frame=frame, point=(x, y), size=4, color=draw_color)
        offset = 5
        y_offset = DrawImage.draw_text(frame=frame, text="Count : " + str(sum(self.count_object.values())), 
                                        point=[offset, offset], color=Color.BLACK)
        DrawImage.draw_text(frame=frame, text="FPS : " + str(avg_fps), 
                             point=[offset, offset*2+y_offset], color=Color.BLACK)