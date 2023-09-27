from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
model_path = ROOT / "models"
if str(model_path) not in sys.path:
    sys.path.append(str(model_path))

class ObjectDetection:
    def __init__(self):
        self.person = [0]
        self.car = [2, 3, 5, 7]
        self.all_obj = self.person + self.car
        with open(ROOT / "class_object" / 'coco.names','rt') as f:
            self.class_name = f.read().rstrip('\n').split('\n')
    
    def select_model(self, model_name="yolo_v6", version="accurate", device="0"):
        weight_path = ROOT / "weights"
        if model_name == "yolo_v6":
            from yolo_v6 import DetectionModel
            if version == "accurate":
                modelWeight = str(weight_path / 'yolov6l6.pt')
            elif version in ["l6", "m6"]:
                modelWeight = str(weight_path / str('yolov6' + version + '.pt'))
            else:
                print(f"model '{model_name}' not has the version '{version}' in system")
                exit()
            
            self.model = DetectionModel(weights=modelWeight, device=device, img_size=[640, 640], half=False)
        else:
            print(f"Not has the model '{model_name}' in system")
            exit()

    def config_model_detection(self, min_scores=0.7, iou_thres=0.5, max_det=1000):
        self.iou_thres = iou_thres
        self.min_scores = min_scores
        self.max_det = max_det

    def detect(self, frame):
        outputs = self.model.compute(frame, conf_thres=self.min_scores, iou_thres=self.iou_thres, 
                                     classes=self.all_obj, agnostic_nms=False, max_det=self.max_det)

        result = []
        for det in outputs:
            classId = det[2]
            cx, cy = map(int, det[0][:2])
            w, h = map(int, det[0][2:])
            obj_info = (cx, cy, int(w/2), int(h/2))
            if classId in self.car:
                result.append(["car", obj_info])
            elif classId in self.person:
                result.append(["person", obj_info])

        return result