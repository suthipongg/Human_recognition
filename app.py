from fastapi import FastAPI, WebSocket
import uvicorn
import os, sys, logging, time
from pathlib import Path
import Config
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

logging.basicConfig(level = logging.INFO)
logging.info("webserver receive image initial")

for file in os.listdir(ROOT / Config.UPLOAD_FOLDER):
    os.remove(ROOT / Config.UPLOAD_FOLDER / file)

app = FastAPI()

cam_info = {}
for cam_id in range(Config.N_CAM):
    cam_info[cam_id] = {"timestamp":0, "save":False, "video":None, "frame":None, "realtime":False}

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

def receive_video(data, cam_id):
    img = preprocess(data['bytes'])
    current_time = round(time.time())
    if not cam_info[cam_id]["save"]:
        cam_info[cam_id]["timestamp"] = current_time
        cam_info[cam_id]["save"] = True
        cam_info[cam_id]["video"] = create_video(cam_id, current_time)
    
    if cam_info[cam_id]["realtime"]:
        cam_info[cam_id]["frame"] = img
    else:
        cam_info[cam_id]["frame"] = None
    cam_info[cam_id]["video"].write(img)
    
    if current_time - cam_info[cam_id]["timestamp"] > Config.video_length_time:
        cam_info[cam_id]["save"] = False
        cam_info[cam_id]["video"].release()
        move_file(name_video(cam_id, cam_info[cam_id]["timestamp"]))

@app.websocket("/upload_image")
async def video_stream(websocket: WebSocket):
    try:
        await websocket.accept()
        cam_id = Config.IP_CONVERTER[websocket.client.host]
        
        while True:
            data = await websocket.receive()
            if 'bytes' in data.keys():
                receive_video(data, cam_id)
                await websocket.send_text(f'timestamp {str(time.time())}: image received')
            elif 'text' in data.keys():
                print(data['text'])
                await websocket.send_text('text received')
            else:
                print("no data")
                await websocket.send_text('wait image')
    except Exception as e:
        print(str(e))
        await websocket.close()
        return str(e), 500
            
@app.websocket('/stream')
async def stream(websocket: WebSocket):
    try:
        await websocket.accept()
        cam_id = Config.IP_CONVERTER[websocket.client.host]
        while True:
            
            if cam_info[cam_id]["frame"] is not None:
                websocket.send_bytes(cam_info[cam_id]["frame"].tobytes())
            else:
                cam_info[cam_id]['realtime'] = True
                websocket.send_text('Wait camera')
    except Exception as e:
        print(str(e))
        await websocket.close()
        cam_id = Config.IP_CONVERTER[websocket.client.host]
        cam_info[cam_id]['realtime'] = False
        return str(e), 500
    
if __name__ == "__main__":
    uvicorn.run("app:app", 
                host='0.0.0.0', 
                port=8080, 
                log_level="info", 
                reload=False
                )