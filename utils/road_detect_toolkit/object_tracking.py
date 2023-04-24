import os
import argparse
import time
from pathlib import Path
import numpy as np

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadImages, letterbox
from utils.general import check_img_size, non_max_suppression, apply_classifier, \
	scale_coords, xyxy2xywh, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized, TracedModel

#parameter
device = 0
weights = ''
img_sz = 640
conf_thres = 0.7
iou_thres = 0.45
classes = [0,1,2,3,5,7,16,17]
agnostic_nms = False
stride, half, model= None, None,None
old_img_w = old_img_h = img_sz
old_img_b = 1

def initialize(weights_path = './weights/yolov7-w6.pt'):
	global stride,half, device, model, weights
	# Initialize
	set_logging()
	device = select_device('0')
	half = device.type != 'cpu'  # half precision only supported on CUDA
	weights = weights_path

	# Load model
	model = attempt_load(weights, map_location=device)  # load FP32 model
	stride = int(model.stride.max())  # model stride
	imgsz = check_img_size(img_sz, s=stride)  # check img_size

	model = TracedModel(model, device, imgsz)
	model.half()

	# Set Dataloader
	vid_path, vid_writer = None, None

	 # Get names and colors
	names = model.module.names if hasattr(model, 'module') else model.names
	colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

	# Run inference
	model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once

def detect(img):
	global old_img_b, old_img_h, old_img_w
	result = []
	im2 = img.copy()

	# Padded resize
	img = letterbox(img, img_sz, stride=stride)[0]

	# Convert
	img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
	img = np.ascontiguousarray(img)


	img = torch.from_numpy(img).to(device)
	img = img.half() if half else img.float()  # uint8 to fp16/32
	img /= 255.0  # 0 - 255 to 0.0 - 1.0
	if img.ndimension() == 3:
		img = img.unsqueeze(0)

	# Warmup
	if (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
		old_img_b = img.shape[0]
		old_img_h = img.shape[2]
		old_img_w = img.shape[3]
		for i in range(3):
			model(img, augment=False)[0]

	# Inference
	t1 = time_synchronized()
	with torch.no_grad():   # Calculating gradients would cause a GPU memory leak
		pred = model(img, augment=False)[0]
	t2 = time_synchronized()

	# Apply NMS
	pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
	t3 = time_synchronized()

	# Process detections
	for i, det in enumerate(pred):  # detections per image
		s, im0= '', im2

		gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
		if len(det):
			# Rescale boxes from img_size to im0 size
			det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

			# Print results
			# for c in det[:, -1].unique():
			# 	n = (det[:, -1] == c).sum()  # detections per class
			# 	s += f"{n} {'s' * (n > 1)}, "  # add to string

			'''
			xyxy: top-left and bottom-right coordinate
			conf: confidence score
			cls: kindd
			'''
			for *xyxy, conf, cls in reversed(det):
				xyxy = [int(xyxy[i]) for i in range(len(xyxy))]
				if xyxy[0] <= 0 or xyxy[1] <= 0 or \
					xyxy[2] >= im0.shape[1] or xyxy[3] >=  im0.shape[0]:
					w = abs(xyxy[0] - xyxy[2])
					h = abs(xyxy[1] - xyxy[3])
					result.append([xyxy[0]+w//2, xyxy[1]+h//2, w, h])
					# cv2.rectangle(im2, (xyxy[0],xyxy[1]), (xyxy[2],xyxy[3]), (0, 0, 255), 2)
					# cv2.circle(im2, (xyxy[0]+w//2, xyxy[1]+h//2), 5, (0, 0, 255), -1)
					# cv2.imwrite('./runs/detect/'+str(frame)+'.jpg',im2)
					# cv2.imshow('l', im2)
					# cv2.waitKey(1)

	print(f'Object Detect Done. ({(1E3 * (t2 - t1)):.1f}ms) Inference, ({(1E3 * (t3 - t2)):.1f}ms) NMS')
	print('objects: ', end='')
	print(result)
	return result

# initialize()
# path = "./runs/detect/exp/origins/"
# frame = 0
# for filename in os.listdir(path):
# 	img = cv2.imread(path + filename)
# 	detect(img, frame)
# 	frame += 1

