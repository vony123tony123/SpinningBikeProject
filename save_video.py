from videoDetect import *
import utils.road_detect_toolkit  as rd

rd.initialize('./weights/yolov7-w6.pt', './cfg/upernet_internimage_l.py', './weights/upernet_internimage_l.pth')
Road_detect()