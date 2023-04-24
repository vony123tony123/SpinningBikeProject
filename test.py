import utils.road_detect_toolkit  as rd
import cv2

rd.initialize('./weights/yolov7-w6.pt', './cfg/upernet_internimage_l.py', './weights/upernet_internimage_l.pth')
img = cv2.imread('./test.jpg')
obstacles, laneLine, img = rd.detect(img, drawPicture=True)
cv2.imshow('l', img)
cv2.waitKey(0)
cv2.destroyAllWindows()