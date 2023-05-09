import cv2
import numpy as np
import threading
import time
import json
import os

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

def Road_detect(video_path = './Data/video_Trim.mp4'):
	global json_arr
	cap = cv2.VideoCapture(video_path)
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
	out = cv2.VideoWriter('output.mp4', fourcc, 20.0,(640,640))
	frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

	yolo_thread = yoloThread()
	lane_thread = laneThread()

	obstacles_list = []
	laneLine_list = []
	json_arr = []
	i = 0

	try:
		while(cap.isOpened()):
			print(f'({i}/{frame_count}) frame from {video_path}')
			ret, frame = cap.read()
			yolo_thread.start(frame)
			lane_thread.start(frame)

			obstacles = yolo_thread.getReturn()
			laneLine = lane_thread.getReturn()

			while (obstacles=="still_working" or laneLine=="still_working"):
				obstacles=yolo_thread.getReturn()
				laneLine=lane_thread.getReturn()
				time.sleep(0.5)

			objects = np.array(obstacles).flatten().tolist()
			dict_input = {'frame':i, 'direction':laneLine[2], 'angle':laneLine[4], 'left_line_range':laneLine[1], 'right_line_range':laneLine[0],'top_point': laneLine[3], 'objects_position':objects}
			json_arr.append(dict_input)
			print(dict_input)
			del dict_input

			frame = rd.drawResult(obstacles, laneLine, frame)
			out.write(frame)
			print('-------')
			i+=1
			if(i>=frame_count):
				break
	except:
		pass

	cap.release()
	out.release()
	cv2.destroyAllWindows()
	txt_path = os.path.splitext(video_path)[0] + '.txt'
	save_json(txt_path)

def save_json(txt_path):
	global json_arr
	if len(json_arr) != 0:
		json_dict = {}
		json_dict['FrameData'] = json_arr
		with open(txt_path, 'w') as file:
				json_input = json.dumps(json_dict,indent=4)
				file.write(json_input)
				del json_input
