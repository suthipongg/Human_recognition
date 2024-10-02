from pathlib import Path
import sys

import torch
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from Configs.config import Config

from ultralytics import YOLO


class ObjectTrackingModel:
    _instance = None

    def __new__(cls, model_path=Config.MODEL_PATH):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize(model_path=model_path)
        return cls._instance

    def initialize(self, model_path=Config.MODEL_PATH):
        self.model = self.load_model(model_path)
        self.car_id = [1, 2, 3, 5, 7]
        self.human_id = [0]
        self.device = torch.device(0 if torch.cuda.is_available() else 'cpu')
        torch.cuda.set_device(self.device)

    def load_model(self, model_path=Config.MODEL_PATH):
        self.model = YOLO(model_path)
        return self.model
    
    def track_data(self, frame, verbose=False):
        results = self.model.track(frame, persist=True, tracker=str(ROOT / 'weights' / Config.TRACKER), classes=[0, 1, 2, 3, 5, 7], verbose=verbose)
        track_id = results[0].boxes.id
        
        if track_id is None:
            return None, None
        
        return results[0].boxes.id, results[0].boxes.cls