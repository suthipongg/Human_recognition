from fastapi import WebSocket, APIRouter
import asyncio
from starlette.websockets import WebSocketState

import sys, logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from Configs.config import Config
from services.redis_service import RedisClient

stream_route = APIRouter(tags=["Report"])

@stream_route.websocket('/stream')
async def stream(websocket: WebSocket):
    try:
        # accept connection
        await websocket.accept()
        cam_id = await websocket.receive_text()
        if not cam_id:
            await websocket.send_text("Chip ID not provided")
            await websocket.close()
            return
        elif cam_id != Config.DEVICE_ID:
            await websocket.send_text("Invalid chip ID")
            await websocket.close()
            return
        RedisClient.set_redis_data('stream', {'status':True})
        logging.info(f"Start streaming cam_id {cam_id}")
        # while connection is open
        while (websocket.application_state == WebSocketState.CONNECTED and websocket.client_state == WebSocketState.CONNECTED):
            base64_frame = RedisClient.get_redis_data('frame').get('frame', None)
            if base64_frame is not None:
                await websocket.send_text(base64_frame)
            else:
                await websocket.send_text('Wait camera')
            await asyncio.sleep(1/Config.FPS)
        await websocket.close()
        RedisClient.set_redis_data('stream', {'status':False})
        RedisClient.clear_redis_data('frame')
        return f"cam_id {cam_id} stopped streaming"
    except Exception as e:
        logging.error(str(e))
        await websocket.send_text('send frame error')
        await websocket.close()
        RedisClient.set_redis_data('stream', {'status':False})
        RedisClient.clear_redis_data(cam_id)
        return str(e), 500