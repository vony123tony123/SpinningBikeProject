import os
from videoDetect import Road_detect, save_json
import utils.road_detect_toolkit  as rd
import atexit
import time
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

def addWaitQueue(video_name):
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

def handle_client(conn, client_name):
    while True:
        try:
            # 接收client傳來的資料
            data = conn.recv(1024)
            if data:
                # 處理unity傳來的資料
                if client_name == 'unity':
                    # 處理 unity 傳來的影片名稱
                    message = data.decode()
                    return_message = 'Add ' + message +' to WaitQueue.'
                    print(return_message)

                    addWaitQueue(message)

                    # 將處理後的結果回傳給unity
                    cilent_unity_socket.send(return_message.encode())
                # 處理client B傳來的資料
                elif client_name == 'raspberry':
                    # 處理 raspberry 
                    message = data.decode()
                    print(message)
                    # speed, cadence, angle = message.split(' ')
                    
                    cilent_unity_socket.send(message.encode())
                    cilent_raspberry_socket.send(message.encode())
        except Exception as e:
            print(e)
            break

    # 關閉連接
    conn.close()
    print(f'{client_name} connection closed')



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
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.settimeout(1)
server_socket.listen(2)

print('server start at: %s:%s' % (ip_address, port_number))
print('wait for connection...')

#等待unity cilent 和 raspberry pi cilent 連接
for i in range(2):
    while True:
        try:
            (client_socket, client_address) = server_socket.accept()
            if client_address[1] == 14786:
                cilent_unity_socket = client_socket
                print('connected to unity by ' + str(client_address))
                client_unity_thread = threading.Thread(target=handle_client, args=(cilent_unity_socket, 'unity'))
                client_unity_thread.daemon = True
                client_unity_thread.start()
                break
            else:
                cilent_raspberry_socket = client_socket
                print('connected to raspberry by ' + str(client_address))
                break
        except socket.timeout:
            continue

# 建立兩個thread處理unity和rasberry的資料
client_raspberry_thread = threading.Thread(target=handle_client, args=(cilent_raspberry_socket, 'raspberry'))
client_raspberry_thread.daemon = True
client_raspberry_thread.start()

while True:
    time.sleep(5)

server_socket.close()

