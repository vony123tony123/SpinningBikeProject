import cv2
import numpy as np
import threading
import time
import json
import os

from pathlib import Path
import utils.road_detect_toolkit  as rd
from utils.general import increment_path

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

def Road_detect(video_path = './Data/30427_hd_Trim.mp4'):
	#Directory
	save_dir = Path(increment_path(Path('runs/detect') / 'exp', exist_ok=False))  # increment run
	(save_dir / 'images').mkdir(parents=True, exist_ok=True)  # make dir

	cap = cv2.VideoCapture(video_path)
	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	video_name = os.path.basename(video_path).split('.')[0]+'.mp4'
	out = cv2.VideoWriter(f'{save_dir}/{video_name}', fourcc, 30.0,(width, height))
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

			result_img = rd.drawResult(obstacles, laneLine, frame)
			out.write(result_img)

			# save Image
			if len(objects) != 0:
				cv2.imwrite(f'{save_dir}/images/{i}.jpg',result_img)

			print('-------')
			i+=1
			if(i>=frame_count):
				break
	except Exception as e:
		print("Exception happened")
		print(e)

	finally:
		cap.release()
		out.release()
		cv2.destroyAllWindows()

		# save json file
		basename = os.path.basename(video_path).split('.')[0] + '.json'
		txt_path = str(save_dir)+ '/' + basename
		print(txt_path)
		save_json(txt_path, json_arr)

		del json_arr

def save_json(txt_path, json_arr):
	if len(json_arr) != 0:
		json_dict = {}
		json_dict['FrameData'] = json_arr
		with open(txt_path, 'w') as file:
				json_input = json.dumps(json_dict,indent=4)
				file.write(json_input)
				del json_input
