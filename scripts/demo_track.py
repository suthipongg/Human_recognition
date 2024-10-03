from tqdm import tqdm
import os, cv2, logging, sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)

ROOT = Path(__file__).resolve().parents[1]
if not os.path.exists(ROOT /'results'):
    os.makedirs(ROOT /'results')

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from Camera.Configs.config import Config
from Object_tracking.modules.tracking_model import ObjectTrackingModel
from Object_tracking.modules.manage_media import LoadVideo

video_path = input("Enter the video path: ")
model = ObjectTrackingModel()
data = {'count': {'car': 0, 'person': 0}, 'frame': {'car': 0, 'person': 0}, 'max_id': {'car': 0, 'person': 0}}
n_car = n_person = 0

def update_data(track_id, class_id):
    global n_car, n_person
    for n, cls in enumerate(class_id):
        if cls in model.car_id and data['max_id']['car'] < track_id[n]:
            data['max_id']['car'] = track_id[n]
            n_car += 1
            data['count']['car'] += 1
        elif cls in model.human_id and data['max_id']['person'] < track_id[n]:
            data['max_id']['person'] = track_id[n]
            n_person += 1
            data['count']['person'] += 1

def write_data(frame, n_car, n_person):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)  # White
    thickness = 2
    line_type = cv2.LINE_AA
    x, y = 10, 30
    line_height = 30    
    cv2.putText(frame, f"Car: {n_car}", (x, y), font, font_scale, font_color, thickness, line_type)
    cv2.putText(frame, f"Person: {n_person}", (x, y+line_height), font, font_scale, font_color, thickness, line_type)
    return frame

video = LoadVideo(video_path)
time_stamp = Path(video_path).stem
result_name = str(ROOT / 'results' / f'{time_stamp}_result.avi')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
width = int(video.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(result_name, fourcc, Config.FPS, (width, height))
logging.info("---> get_track_data")
for frame in tqdm(video):
    boxes = model.track_data(frame, verbose=False)
    
    if boxes is None:
        frame = write_data(frame, n_car, n_person)
        out.write(frame)
        continue
    track_id, class_id = boxes.id, boxes.cls
    update_data(track_id, class_id)
    color = (255, 0, 0)
    thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX
    for i, box in enumerate(boxes):
        start_point = tuple([int(p) for p in box.xyxy[0, :2]])
        end_point = tuple([int(p) for p in box.xyxy[0, 2:]])
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        frame = cv2.putText(frame, f"id: {int(box.id)}", start_point, font, 1, (0, 0, 255), thickness)
    frame = write_data(frame, n_car, n_person)
    out.write(frame)
    
    data['frame']['car'] = max(data['frame']['car'], n_car)
    data['frame']['person'] = max(data['frame']['person'], n_person)
out.release()

for i in data['count']:
    logging.info(f"{i}: {data['count'][i]}")