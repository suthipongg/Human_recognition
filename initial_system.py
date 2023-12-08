import os
import Config

ls_dir = [
    Config.VIDEO_ROOT, 
    Config.UPLOAD_FOLDER, 
    Config.VIDEO_TEMP_FOLDER, 
    Config.VIDEO_PROCESS_FOLDER, 
    Config.VIDEO_PREVIOUS, 
    Config.DATA_TRACKING_FOLDER,
    ]

def create_dir(ls_path):
    for dir in ls_path:
        if not os.path.exists(dir):
            os.makedirs(dir)

def create_json(reset=False):
    for cam_id in range(Config.N_CAM):
        if not os.path.exists(Config.DATA_TRACKING_FOLDER / (str(cam_id)+'.json')) or reset:
            with open(Config.DATA_TRACKING_FOLDER / (str(cam_id)+'.json'), 'w') as f:
                f.write('{"car":0,"person":0}')

if __name__ == '__main__':
    create_dir(ls_dir)
    
    for ng in range(Config.N_GPU):
        if not os.path.exists(Config.VIDEO_PROCESS_FOLDER / str(ng)):
            os.makedirs(Config.VIDEO_PROCESS_FOLDER / str(ng))

    create_json()