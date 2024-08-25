from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketState
import uvicorn
import os, sys, logging, time
from pathlib import Path
import nvdia_jetson.Camera.Configs.environment as environment
import cv2
import numpy as np
import asyncio
import base64
from scripts.redis_controller import check_redis_connection, get_redis_data, set_redis_data, clear_redis_data

if not check_redis_connection:
    exit()

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

logging.basicConfig(level = logging.INFO)
logging.info("stream service")

app = FastAPI()

# decode image data from espcam
def preprocess(img):
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    return img

@app.websocket('/stream')
async def stream(websocket: WebSocket):
    try:
        # accept connection
        await websocket.accept()
        cam_id = await websocket.receive_text()
        if not cam_id:
            await websocket.send_text("Chip ID not provided")
            await websocket.close()
            return
        elif cam_id != environment.DEVICE_ID:
            await websocket.send_text("Invalid chip ID")
            await websocket.close()
            return
        set_redis_data('stream', {'status':True})
        print(f"Start streaming cam_id {cam_id}")
        # while connection is open
        while (websocket.application_state == WebSocketState.CONNECTED and websocket.client_state == WebSocketState.CONNECTED):
            # if frame is saved in memory, send frame to servers
            base64_frame = get_redis_data(cam_id)
            if base64_frame is not None:
                # _, buffer = cv2.imencode('.jpg', frame)
                # base64_frame = base64.b64encode(buffer).decode("utf-8")
                await websocket.send_text(base64_frame.get('frame'))
            # if frame is not saved in memory, send text to server
            else:
                await websocket.send_text('Wait camera')
            await asyncio.sleep(1)
        await websocket.close()
        set_redis_data('stream', {'status':False})
        clear_redis_data(cam_id)
        return f"cam_id {cam_id} stopped streaming"
    except Exception as e:
        print(str(e))
        await websocket.send_text('send frame error')
        await websocket.close()
        set_redis_data('stream', {'status':False})
        clear_redis_data(cam_id)
        return str(e), 500
    
if __name__ == "__main__":
    uvicorn.run("app:app", 
                host='0.0.0.0', 
                port=8080, 
                log_level="info", 
                reload=False
                )