import cv2
from scripts.object_detection import ObjectDetection
import math

class Tracking:
    def __init__(self):
        self.set_init_info()

    def set_init_info(self):
        self.center_points_cur_frame = [] # contain class_obj, point xywh
        self.center_points_cur_frame_remain = []
        self.tracking_objects = {} # contain class_obj, point xywh, confident, out_of_frame
        self.track_id = 0
        self.frame = 0
        self.count_person = 0

    def config_tracking(self, max_movement=20, min_scores=0.7, min_confidence_obj=2, min_out_of_frame=2):
        self.max_movement = max_movement
        self.min_scores = min_scores
        self.min_confidence_obj = max(0, min_confidence_obj-1)
        self.min_out_of_frame = max(0, min_out_of_frame-1)

    def select_model_detection(self, model_name, version):
        self.model = ObjectDetection(model_name, version)
        self.model.select_model()

    def open_video(self, video):
        self.cap = cv2.VideoCapture(video)

    def get_amount_person(self):
        return self.count_person

    def __start_loop(self):
        self.center_points_prev_frame = self.center_points_cur_frame
        self.center_points_cur_frame = []
        ret, self.frame = self.cap.read()
        # self.frame = cv2.resize(self.frame, (800, 600), interpolation = cv2.INTER_AREA)
        return ret

    def __kill_process(self):
        return cv2.waitKey(1) == 27
    
    def __detect_object(self):
        self.frame, self.center_points_cur_frame = self.model.detect(self.frame, self.min_scores)

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

    def __confident_in_frame(self, confident, object_id, pt_min_dist):
        self.tracking_objects[object_id][1] = pt_min_dist # point 
        self.center_points_cur_frame_remain.remove(self.tracking_objects[object_id][0:2])
        self.tracking_objects[object_id][3] = 0 # out_of_frame
        if confident < self.min_confidence_obj:
            self.tracking_objects[object_id][2] += 1 # confident
        elif confident == self.min_confidence_obj:
            self.count_person += 1
            self.tracking_objects[object_id][2] += 1 # confident

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

    def __put_text_image(self, name_frame="Frame"):
        for object_id, obj_info in self.tracking_objects.items():
            class_obj, pt, confident, out_of_frame = obj_info
            cv2.circle(self.frame, (pt[0], pt[1]), 5, (0, 0, 255), -1)
        for obj_info in self.center_points_cur_frame:
            class_obj, pt = obj_info
            cv2.putText(self.frame, class_obj, (pt[0]-pt[2], pt[1]-pt[3]), 0, 0.5, (0, 0, 255), 2)
        cv2.putText(self.frame, "count : " + str(self.count_person), (0, 30), 0, 1, (0, 0, 255), 2)
        cv2.imshow(name_frame, self.frame)

    def __clear_process(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def start_track(self):
        while 1:
            if not self.__start_loop() or self.__kill_process():
                break
            self.__detect_object()

            self.__search_old_ID()
            self.__add_new_ID()

            self.__put_text_image()

        self.__clear_process()
        return self.get_amount_person()