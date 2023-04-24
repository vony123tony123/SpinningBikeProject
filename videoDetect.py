import cv2
import numpy as np
import threading
import time
import json

import utils.road_detect_toolkit  as rd

class yoloThread():
	def start(self, img):
		self.img = img
		self.thread = threading.Thread(target=self.detect, args=())
		self.thread.daemon=True
		self.thread.start()
		self.switch = True
	
	def detect(self):
		self.yoloPred = rd.obstaclePred(self.img)
		self.switch = False

	def getReturn(self):
		if self.switch:
			return "still_working"
		else:
			return self.yoloPred

class laneThread():
	def start(self, img):
		self.img = img
		self.thread = threading.Thread(target=self.detect, args=())
		self.thread.daemon=True
		self.thread.start()
		self.switch = True
	
	def detect(self):
		self.lanePred = rd.laneLinePred(self.img)
		self.switch = False

	def getReturn(self):
		if self.switch:
			return "still_working"
		else:
			return self.lanePred

rd.initialize('./weights/yolov7-w6.pt', './cfg/upernet_internimage_l.py', './weights/upernet_internimage_l.pth')
cap = cv2.VideoCapture('./30427_hd_Trim.mp4')
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

yoloThread = yoloThread()
laneThread = laneThread()

obstacles_list = []
laneLine_list = []
json_arr = []
i = 0

try:
	while(cap.isOpened()):
		print(f'({i}/{frame_count}) frame')
		ret, frame = cap.read()
		yoloThread.start(frame)
		laneThread.start(frame)

		obstacles = yoloThread.getReturn()
		laneLine = laneThread.getReturn()

		while (obstacles=="still_working" or laneLine=="still_working"):
			obstacles=yoloThread.getReturn()
			laneLine=laneThread.getReturn()
			time.sleep(0.5)

		objects = np.array(obstacles).flatten().tolist()
		dict_input = {'frame':i, 'direction':laneLine[2], 'angle':laneLine[4], 'left_line_range':laneLine[1], 'right_line_range':laneLine[0],'top_point': laneLine[3], 'objects_position':objects}
		json_arr.append(dict_input)
		print(dict_input)
		del dict_input

		# frame = rd.drawResult(obstacles, laneLine, frame)
		# cv2.imshow('l', frame)
		# cv2.waitKey(1)
		print(f'len(json_arr) = {len(json_arr)}')
		print('-------')
		i+=1
		if(i>=frame_count):
			break
except:
	cap.release()
	cv2.destroyAllWindows()
	json_dict = {}
	json_dict['FrameData'] = json_arr
	with open("test.json", 'w') as file:
		json_input = json.dumps(json_dict,indent=4)
		file.write(json_input)
		del json_input

cap.release()
cv2.destroyAllWindows()
json_dict = {}
json_dict['FrameData'] = json_arr
with open("test.json", 'w') as file:
		json_input = json.dumps(json_dict,indent=4)
		file.write(json_input)
		del json_input
