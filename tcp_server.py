import os
from videoDetect import Road_detect, save_json
import utils.road_detect_toolkit  as rd
import atexit
import threading
import socket

class detectThread():
    wait_list = []
    def start(self):
        self.thread = threading.Thread(target=self.detect, args=())
        self.thread.daemon=True
        self.thread.start()
    
    def detect(self):
        atexit.register(self.on_exit)
        while True:
            if len(self.wait_list) == 0:
                continue
            video_path = self.wait_list[0]
            Road_detect(video_path)
            self.wait_list.pop(0)

    def add_video(self, video_path):
        global wait_list
        self.wait_list.append(video_path)

    def on_exit(self):
        video_path = self.wait_list[0]
        save_json(os.path.splitext(video_path)[0] + '.txt')
    
    def get_waitList(self):
        return self.wait_list

def detect(video_name):
    global loaded_model, detect_thread
    try:
        if loaded_model == False:
            rd.initialize('./weights/yolov7-w6.pt', './cfg/upernet_internimage_l.py', './weights/upernet_internimage_l.pth')
            detect_thread.start()
            loaded_model = True
        video_path = os.path.join(video_base_path, video_name)
        detect_thread.add_video(video_path)
        return detect_thread.get_waitList()
    except Exception as e:
        raise


video_base_path = "./Data/"
loaded_model = False
detect_thread = detectThread()

# 建立一個 IPv4 和 TCP 的socket物件
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 設定IP位址和埠號
ip_address = '127.0.0.1'
port_number = 30000

# 將socket繫結到指定IP和埠號
server_socket.bind((ip_address, port_number))
server_socket.listen()
server_socket.settimeout(1)

print('server start at: %s:%s' % (ip_address, port_number))
print('wait for connection...')

while True:
    try:
        # 等待連線，並返回一個與客戶端連接的socket物件
        (client_socket, client_address) = server_socket.accept()
        print('connected by ' + str(client_address))

        # 接收客戶端發送的資料
        data = client_socket.recv(1024)

        message = data.decode()
        return_message = 'Add ' + message +' to WaitQueue.'
        print(return_message)

        detect(message)

        client_socket.send(return_message.encode())
        client_socket.close()
    except socket.timeout:
        continue
    except:
        raise
        break

server_socket.close()

