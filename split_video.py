import cv2

cap = cv2.VideoCapture("./video_Trim.mp4")
i = 0
while cap.isOpened():
	ret, frame = cap.read()
	i += 1
	if i%6 == 0:
		cv2.imwrite("./video_images/video_Trim_"+str(i)+".jpg", frame)
		print(i)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()