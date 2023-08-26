from scripts.object_tracking import Tracking

det = Tracking()
det.config_tracking(max_movement=300, min_scores=0.6, min_confidence_obj=5, min_out_of_frame=20)
det.select_model_detection("yolo_v3", "accurate")
det.open_video("video/walking.avi")
count = det.start_track()
print("count :", count)