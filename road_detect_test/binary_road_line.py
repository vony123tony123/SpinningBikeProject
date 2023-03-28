import cv2
import numpy as np

img_path = "D:/Project/SpinningBikeProject/Data/video_images/30427_hd_Trim_Trim/10.jpg"

img = cv2.imread(img_path)

lower = np.array([255,0,0])
upper = np.array([255,255,255])
mask = cv2.inRange(img, lower, upper)

output = cv2.bitwise_and(img, img, mask = mask )

cv2.namedWindow("demo")
cv2.imshow("demo",mask)
cv2.waitKey(0)