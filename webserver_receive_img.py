from flask import Flask, request
import os, sys
from pathlib import Path
import time
import Config
import cv2
import numpy as np
import logging

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

app = Flask(__name__)

cam_info = {}
for cam_id in range(Config.N_CAM):
    cam_info[cam_id] = {"timestamp":0, "save":False, "video":None}

# video_name = timestamp_camID.ExtName
def name_video(cam_id, current_time):
    return str(current_time) + "_" + str(cam_id) + Config.EXT_VIDEO

def create_video(cam_id, current_time):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    file_name = name_video(cam_id, current_time)
    out = cv2.VideoWriter(str(ROOT / Config.UPLOAD_FOLDER / file_name), fourcc, Config.FPS, (Config.WIDTH, Config.HEIGHT))
    return out

def preprocess(img):
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img

def move_file(file):
    src_file = Path(ROOT / Config.UPLOAD_FOLDER / file)
    dst_file = Path(ROOT / Config.VIDEO_TEMP_FOLDER / file)
    src_file.rename(dst_file)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        image_data = request.data
        cam_id = Config.IP_CONVERTER[request.remote_addr]
        if image_data:
            img = preprocess(image_data)

            current_time = round(time.time())
            if not cam_info[cam_id]["save"]:
                cam_info[cam_id]["timestamp"] = current_time
                cam_info[cam_id]["save"] = True
                cam_info[cam_id]["video"] = create_video(cam_id, current_time)
                
            cam_info[cam_id]["video"].write(img)
            
            if current_time - cam_info[cam_id]["timestamp"] > Config.video_length_time:
                cam_info[cam_id]["save"] = False
                cam_info[cam_id]["video"].release()
                move_file(name_video(cam_id, cam_info[cam_id]["timestamp"]))
                
            return "Image uploaded and processed successfully.", 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    logging.info("webserver receive image initial")
    
    for file in os.listdir(ROOT / Config.VIDEO_ROOT / Config.VIDEO_TEMP_FOLDER):
        if file.endswith(Config.EXT_VIDEO):
            file.rename(ROOT / Config.VIDEO_PROCESS_FOLDER / file)
    
    app.run(host='0.0.0.0', port=8080)
