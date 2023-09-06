#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import cv2
import math
import torch
import numpy as np

from pathlib import Path
import sys

yolo_v6 = Path(__file__).resolve().parents[0] / Path(__file__).stem
if str(yolo_v6) not in sys.path:
    sys.path.append(str(yolo_v6))

from yolov6.layers.common import DetectBackend
from yolov6.data.data_augment import letterbox
from yolov6.utils.nms import non_max_suppression

class detect:
    def __init__(self, weights, device, img_size, half):
        self.__dict__.update(locals())

        # Init model
        self.device = device
        self.img_size = img_size
        cuda = self.device != 'cpu' and torch.cuda.is_available()
        self.device = torch.device(f'cuda:{device}' if cuda else 'cpu')
        self.model = DetectBackend(weights, device=self.device)
        self.stride = self.model.stride
        self.img_size = self.check_img_size(self.img_size, s=self.stride)  # check image size
        self.half = half

        # Switch model to deploy status
        self.model_switch(self.model.model)

        # Half precision
        if self.half & (self.device.type != 'cpu'):
            self.model.model.half()
        else:
            self.model.model.float()
            self.half = False

        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, *self.img_size).to(self.device).type_as(next(self.model.model.parameters())))  # warmup

    def model_switch(self, model):
        ''' Model switch to deploy status '''
        from yolov6.layers.common import RepVGGBlock
        for layer in model.modules():
            if isinstance(layer, RepVGGBlock):
                layer.switch_to_deploy()
            elif isinstance(layer, torch.nn.Upsample) and not hasattr(layer, 'recompute_scale_factor'):
                layer.recompute_scale_factor = None  # torch 1.11.0 compatibilit

    def compute(self, frame, conf_thres, iou_thres, classes, agnostic_nms, max_det):
        ''' Model Inference and results visualization '''
        img = self.process_image(frame, self.img_size, self.stride, self.half)
        img = img.to(self.device)
        if len(img.shape) == 3:
            img = img[None]
            # expand for batch dim
        pred_results = self.model(img)
        det = non_max_suppression(pred_results, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)[0]
        img_ori = frame.copy()

        output = []
        if len(det):
            det[:, :4] = self.rescale(img.shape[2:], det[:, :4], frame.shape).round()
            for *xyxy, conf, cls in det:
                xywh = (self.box_convert(torch.tensor(xyxy).view(1, 4))).view(-1).tolist()  # normalized xywh
                class_num = int(cls)  # integer class
                output.append([xywh, float(conf), class_num])

            frame = np.asarray(img_ori)
        return output

    @staticmethod
    def process_image(img_src, img_size, stride, half):
        '''Process image before image inference.'''
        image = letterbox(img_src, img_size, stride=stride)[0]
        # Convert
        image = image.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        image = torch.from_numpy(np.ascontiguousarray(image))
        image = image.half() if half else image.float()  # uint8 to fp16/32
        image /= 255  # 0 - 255 to 0.0 - 1.0
        return image

    @staticmethod
    def rescale(ori_shape, boxes, target_shape):
        '''Rescale the output to the original image shape'''
        ratio = min(ori_shape[0] / target_shape[0], ori_shape[1] / target_shape[1])
        padding = (ori_shape[1] - target_shape[1] * ratio) / 2, (ori_shape[0] - target_shape[0] * ratio) / 2

        boxes[:, [0, 2]] -= padding[0]
        boxes[:, [1, 3]] -= padding[1]
        boxes[:, :4] /= ratio

        boxes[:, 0].clamp_(0, target_shape[1])  # x1
        boxes[:, 1].clamp_(0, target_shape[0])  # y1
        boxes[:, 2].clamp_(0, target_shape[1])  # x2
        boxes[:, 3].clamp_(0, target_shape[0])  # y2

        return boxes

    def check_img_size(self, img_size, s=32, floor=0):
        """Make sure image size is a multiple of stride s in each dimension, and return a new shape list of image."""
        if isinstance(img_size, int):  # integer i.e. img_size=640
            new_size = max(self.make_divisible(img_size, int(s)), floor)
        elif isinstance(img_size, list):  # list i.e. img_size=[640, 480]
            new_size = [max(self.make_divisible(x, int(s)), floor) for x in img_size]
        else:
            raise Exception(f"Unsupported type of img_size: {type(img_size)}")

        if new_size != img_size:
            print(f'WARNING: --img-size {img_size} must be multiple of max stride {s}, updating to {new_size}')
        return new_size if isinstance(img_size,list) else [new_size]*2

    def make_divisible(self, x, divisor):
        # Upward revision the value x to make it evenly divisible by the divisor.
        return math.ceil(x / divisor) * divisor

    @staticmethod
    def box_convert(x):
        # Convert boxes with shape [n, 4] from [x1, y1, x2, y2] to [x, y, w, h] where x1y1=top-left, x2y2=bottom-right
        y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
        y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
        y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
        y[:, 2] = x[:, 2] - x[:, 0]  # width
        y[:, 3] = x[:, 3] - x[:, 1]  # height
        return y
 
@torch.no_grad()
def test():
    w = "/home/mew/Desktop/Object_tracking/weights/yolov6l6.pt"
    s = "/home/mew/Desktop/Object_tracking/video/cars.avi"
    data = "/home/mew/Desktop/Object_tracking/models/yolo_v6/data/coco.yaml"
    c = [0,2,3,5,7]
    inferer = detect(weights=w, device='0', img_size=[640, 640], half=False)
    cap = cv2.VideoCapture(s)
    while 1:
        ret_val, img = cap.read()
        inferer.compute(img, conf_thres=0.4, iou_thres=0.45, classes=c, agnostic_nms=False, max_det=1000, )
        if cv2.waitKey(1)  == 27: break

if __name__ == "__main__":
    test()