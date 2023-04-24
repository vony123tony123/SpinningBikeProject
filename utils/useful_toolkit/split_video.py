import cv2

cap = cv2.VideoCapture("./30427_hd_Trim.mp4")
i = 0
while cap.isOpened():
	ret, frame = cap.read()
	i += 1
	if i%10 == 0:
		cv2.imwrite("./Data/video_images/30427_hd_Trim/Trim_"+str(i)+".jpg", frame)
		print(i)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
cv2.destroyAllWindows()