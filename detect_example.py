from scripts.object_tracking import Tracking
import torch
@torch.no_grad()
def test():
    det = Tracking()
    det.config_model_detection(min_scores=0.4, iou_thres=0.5)
    det.config_tracking(max_movement=1000, min_confidence_obj=5, min_out_of_frame=20)
    det.select_model_detection("yolo_v6", "l6")
    det.open_video("/home/mew/Desktop/Object_tracking/video/walking.avi")
    count = det.start_track(view_image=True)
    print("count :", count)
test()