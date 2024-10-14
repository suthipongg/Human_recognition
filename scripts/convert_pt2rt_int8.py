from ultralytics import YOLO
from pathlib import Path

ROOT = Path(__file__).parent.parent

model = YOLO(ROOT / "Object_tracking" / "weights" / "yolov8n.pt")
model.export(
    format="engine",
    dynamic=True,  
    batch=8,  
    workspace=4,  
    int8=True,
    data="coco.yaml",  
)