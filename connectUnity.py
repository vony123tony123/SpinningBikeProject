import numpy
import cv2
import socket
import json

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
resolutionRatio = 50

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (TCP_IP ,TCP_PORT)
print(address)
sock.connect(address)

print("initial")
sock.send('Connect Check'.encode('utf-8'))

sock.close()

cap = cv2.VideoCapture('D:/Banana/coding/Unity/temp.mp4')
params = [cv2.IMWRITE_JPEG_QUALITY, resolutionRatio]
while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        break
    img = cv2.resize(img,(1280,720))
    img_data = {'image':cv2.imencode('.jpg', img, params)[1].ravel().tolist()}
    data = json.dumps(img_data)
    # print(data)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    
    sock.sendall(bytes(data,encoding='utf-8'))
    # print("sent")
    
    cv2.imshow("Image", img)
    cv2.waitKey(10)

print("out")
recdata = sock.recv(1024)
print(recdata.decode())
sock.close()
    # print("close")
    
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect(address)
    
    # sock.close()
    
