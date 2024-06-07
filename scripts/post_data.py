import sys, requests
from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import Config

def post_camera(cam_id, data, timestamp):
    body_data = {}
    body_data['camId'] = "CAM_" + str(cam_id)
    body_data['personCount'] = data['person']
    body_data['carCount'] = data['car']
    body_data['published'] = True
    body_data['timeDevice'] = timestamp
    logging.info(body_data)
    requests.post(Config.POST_URL['camera'], json=body_data)
    
def post_frame(cam_id, data, timestamp):
    body_data = {}
    body_data['camId'] = "CAM_" + str(cam_id)
    body_data['personInFrame'] = data['person']
    body_data['carInFrame'] = data['car']
    body_data['published'] = True
    body_data['timeDevice'] = timestamp
    logging.info(body_data)
    requests.post(Config.POST_URL['frame'], json=body_data)