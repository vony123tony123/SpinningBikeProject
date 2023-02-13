import cv2

cap = cv2.VideoCapture("./video_Trim.mp4")
i = 0
while cap.isOpened():
	ret, frame = cap.read()
	cv2.imwrite("./video_image/video_Trim_"+str(i)+".jpg", frame)
	i += 1
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()