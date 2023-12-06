import os
import Config


if not os.path.exists(Config.VIDEO_ROOT):
    os.makedirs(Config.VIDEO_ROOT)
    
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)
    
if not os.path.exists(Config.VIDEO_TEMP_FOLDER):
    os.makedirs(Config.VIDEO_TEMP_FOLDER)
    
if not os.path.exists(Config.VIDEO_PROCESS_FOLDER):
    os.makedirs(Config.VIDEO_PROCESS_FOLDER)
    
if not os.path.exists(Config.VIDEO_PREVIOUS):
    os.makedirs(Config.VIDEO_PREVIOUS)

if not os.path.exists(Config.DATA_TRACKING_FOLDER):
    os.makedirs(Config.DATA_TRACKING_FOLDER)
    
for ng in range(Config.N_GPU):
    if not os.path.exists(Config.VIDEO_PROCESS_FOLDER / str(ng)):
        os.makedirs(Config.VIDEO_PROCESS_FOLDER / str(ng))

for id in range(Config.N_CAM):
    if not os.path.exists(Config.DATA_TRACKING_FOLDER / (str(id)+'.json')):
        with open(Config.DATA_TRACKING_FOLDER / (str(id)+'.json'), 'w') as f:
            f.write('{"car":0,"person":0}')