import utils.road_detect_toolkit.lane_line_detect as lane_detect
import utils.road_detect_toolkit.object_tracking as obstacle_detect
import cv2

def launch_yolo_model(yPath):
	obstacle_detect.initialize(yPath)

def launch_laneLine_model(cfgpath, checkpointpath):
	lane_detect.initialize(config=cfgpath, checkpoint=checkpointpath)

def obstaclePred(img):
	return obstacle_detect.detect(img)

def laneLinePred(img):
	return lane_detect.img_seg(img)

def drawResult(obstacles, laneLine, img):
	# draw obstacles
	if len(obstacles) != 0:
		for obstacle in obstacles:
			x,y,w,h = obstacle
			cv2.rectangle(img, (x-w//2, y-h//2), (x+w//2, y+h//2), (0, 0, 255), 2)

	# draw road line
	cv2.line(img, (laneLine[0][0], laneLine[0][1]), (laneLine[0][2], laneLine[0][3]), (255, 0, 0), 2)
	cv2.line(img, (laneLine[1][0], laneLine[1][1]), (laneLine[1][2], laneLine[1][3]), (255, 0, 0), 2)

	# draw direction line
	imshape = img.shape
	cv2.line(img, (imshape[1]//2, imshape[0]), (laneLine[3][0], laneLine[3][1]), (255, 255, 0), 2)

	text = laneLine[2]
	font = cv2.FONT_HERSHEY_SIMPLEX
	font_scale = 1
	thickness = 2
	text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
	cv2.putText(img, text, (10, text_size[1]+10), font, font_scale, (0, 0, 255), thickness)
	
	return img

def initialize(yPath, cfgpath, checkpointpath):
	launch_yolo_model(yPath)
	launch_laneLine_model(cfgpath, checkpointpath)

def detect(img, drawPicture=False):
	obstacles = obstaclePred(img)
	laneLine = laneLinePred(img)
	if drawPicture:
		img = drawResult(obstacles, laneLine, img)
	return obstacles, laneLine, img