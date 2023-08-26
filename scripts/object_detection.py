import cv2
import numpy as np
import pathlib

from time import time

class ObjectDetection:
    def __init__(self, model_name="yolo_v3", version="fast"):
        self.model_name = model_name
        self.version = version
    
    def select_model(self):
        file_path = pathlib.Path(__file__).parents[1]
        weight_path = file_path / "weights"
        if self.model_name == "yolo_v3":
            self.person = [0]
            self.car = [3, 4, 6, 8]
            self.all_obj = self.person + self.car
            if self.version == "fast":
                modelConfig = weight_path / 'yolov3.cfg'
                modelWeight = weight_path / 'yolov3.weights'
            elif self.version == "accurate":
                modelConfig = weight_path / 'yolov3-spp.cfg'
                modelWeight = weight_path / 'yolov3-spp.weights'
            else:
                print(f"model '{self.model_name}' not has the version '{self.version}' in system")
                exit()

            with open(file_path / "class_object" / 'coco.names','rt') as f:
                self.class_name = f.read().rstrip('\n').split('\n')
            
            self.model = cv2.dnn.readNetFromDarknet(str(modelConfig),str(modelWeight))
            self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU_FP16)
        else:
            print(f"Not has the model '{self.model_name}' in system")
            exit()

    def detect(self, frame, min_score):
        whT=320
        blob = cv2.dnn.blobFromImage(frame,1/255,(whT,whT),[0,0,0],1,crop=False)
        self.model.setInput(blob)
        outputNames = [i for i in self.model.getUnconnectedOutLayersNames()]
        outputs = self.model.forward(outputNames)

        # clean object that low confident and object class
        hT, wT, cT = frame.shape
        temp, result = [], []
        bbox, confs = [], []
        for output in outputs:
            for det in output:
                scores = det[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > min_score and classId in self.all_obj:
                    cx, cy = int(det[0]*wT), int(det[1]*hT)
                    w, h = int(det[2]*wT), int(det[3]*hT)
                    x, y = int(cx-w/2), int(cy-h/2)
                    bbox.append([x,y,w,h])
                    confs.append(float(confidence))
                    obj_info = (cx, cy, int(w/2), int(h/2))
                    if classId in self.car:
                        temp.append(["car", obj_info])
                    elif classId in self.person:
                        temp.append(["person", obj_info])

        # clean box that overlap
        indices = cv2.dnn.NMSBoxes(bbox,confs,min_score,0.3)
        for i in indices:
            result.append(temp[i])
            x, y, w, h = bbox[i]
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,255),2)
        # class_name = self.classNames[classIds[i]].upper()
        return frame, result

if __name__ == "__main__":
    ob = ObjectDetection()