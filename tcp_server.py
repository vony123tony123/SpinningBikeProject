import os
from videoDetect import Road_detect, save_json
import utils.road_detect_toolkit  as rd
import atexit
import time
import datetime
import threading
import socket
import json
import traceback

unity_connect = False
raspberry_connect = False
threads_stop = False

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
        with open('WaitQueue_log.txt', 'a') as f:
            now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(now_formatted + ' : '+ str(detect_thread.get_waitList()) + '\n')
        return detect_thread.get_waitList()
    except Exception as e:
        raise

def unity_handle(conn):
    global unity_connect, raspberry_connect
    conn.send('OK'.encode())
    while True:
        try:
            # 接收client傳來的資料
            data = conn.recv(1024)

            # 處理 unity 傳來的影片名稱
            message = data.decode()

            print(message)

            with open('unity_log.txt', 'a') as f:
                now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(now_formatted + ' : '+ message + '\n')

            if message == "Disconnect":
                return_message = "Close socket"
                conn.send(return_message.encode())
                raise Exception("accept unity disconnect request")
            else:
                return_message = 'Add ' + message +' to WaitQueue.'
                # addWaitQueue(message)

                # 將處理後的結果回傳給unity
                conn.send(return_message.encode())

        except Exception as e:
            unity_connect = False
            print(e)
            # 關閉連接
            conn.close()
            print(f'Unity thread closed')
            break
        
def rasberry_handle(conn):
    global unity_connect, raspberry_connect
    try:
        while True:
            # 接收client傳來的資料
            data = conn.recv(1024)

            # 處理 raspberry 
            message = data.decode()

            print(message)
            
            with open('RasberryRecieve_log.txt', 'a') as f:
                now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(now_formatted + ' : '+ message + '\n')
            
            if unity_connect == True:
                cilent_unity_socket.send(data)
            client_raspberry_socket.send(data)
    except Exception as e:
        raspberry_connect = False
        print(e)
        # 關閉連接
        conn.close()
        print(f'Raspberry thread closed')

# def handle_client(conn, client_name):
    # while True:
    #     try:
    #         # 接收client傳來的資料
    #         data = conn.recv(1024)
            
    #         if data:
    #             print(data)
    #             # 處理unity傳來的資料
    #             if client_name == 'unity':
    #                 # 處理 unity 傳來的影片名稱
    #                 message = data.decode()

    #                 with open('unity_log.txt', 'a') as f:
    #                     now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                     f.write(now_formatted + ' : '+ message + '\n')

    #                 if message == "Disconnect":
    #                     return_message = "Close socket"
    #                     cilent_unity_socket.send(return_message.encode())
    #                     raise Exception("accept unity disconnect request")
    #                 else:
    #                     return_message = 'Add ' + message +' to WaitQueue.'
    #                     # addWaitQueue(message)

    #                     # 將處理後的結果回傳給unity
    #                     cilent_unity_socket.send(return_message.encode())
                        
    #             # 處理raspberry傳來的資料
    #             elif client_name == 'raspberry':
    #                 # 處理 raspberry 
    #                 message = data.decode()
                    
    #                 with open('RasberryRecieve_log.txt', 'a') as f:
    #                     now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                     f.write(now_formatted + ' : '+ message + '\n')
                    
    #                 if unity_connect == True:
    #                     cilent_unity_socket.send(data)
    #                 client_raspberry_socket.send(data)
    #     except Exception as e:
    #         traceback.print_exc()
    #         # 關閉連接
    #         conn.close()
    #         print(f'{client_name} connection closed')
    #         break


video_base_path = "./Data/"
loaded_model = False
detect_thread = detectThread()

# 建立一個 IPv4 和 TCP 的socket物件
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 設定IP位址和埠號
ip_address = '192.168.100.145'
port_number = 30000

# 將socket繫結到指定IP和埠號
server_socket.bind((ip_address, port_number))
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.settimeout(1)
server_socket.listen(2)

print('server start at: %s:%s' % (ip_address, port_number))
print('wait for connection...')

# while True:
#     try:
#         #等待unity cilent 和 raspberry pi cilent 連接
#         for i in range(2):
#             while True:
#                 try:
#                     (client_socket, client_address) = server_socket.accept()
#                     #暫定unity的port 為14786，如果要測試記得改
#                     if client_address[0] == ip_address:
#                         cilent_unity_socket = client_socket
#                         print('connected to unity by ' + str(client_address))
#                         client_unity_thread = threading.Thread(target=handle_client, args=(cilent_unity_socket, 'unity'))
#                         client_unity_thread.daemon = True
#                         unity_connect = True
#                         break
#                     else:
#                         client_raspberry_socket = client_socket
#                         print('connected to raspberry by ' + str(client_address))
#                         raspberry_connect = True
#                         client_raspberry_thread = threading.Thread(target=handle_client, args=(client_raspberry_socket, 'raspberry'))
#                         client_raspberry_thread.daemon = True
#                         client_raspberry_thread.start()
#                         break
#                 except socket.timeout:
#                     continue

#         # 最後需要回傳給unity所以要等unity_socket到了才能執行       
         
#         # cilent_unity_socket.send('OK'.encode())
#         # client_unity_thread.start()

#         while True:
#             time.sleep(5)
#             if not (client_raspberry_thread.is_alive() and client_unity_thread.is_alive()):
#                 raise Exception('unity or raspberry shutdown')


#     except Exception as e:
#         print(e)
#         try:
#             cilent_unity_socket.close()
#         except Exception as e:
#             print(e)
#             pass

#         try:
#             client_raspberry_socket.close()
#         except Exception as e:
#             print(e)
#             pass
#         continue

while True:
    #等待unity cilent 和 raspberry pi cilent 連接
    try:
        (client_socket, client_address) = server_socket.accept()
        if client_address[0] == ip_address:
            unity_connect = True
            cilent_unity_socket = client_socket
            print('connected to unity by ' + str(client_address))
            client_unity_thread = threading.Thread(target=unity_handle, args=(cilent_unity_socket, ))
            client_unity_thread.daemon = True
            client_unity_thread.start()
        else:
            raspberry_connect = True
            client_raspberry_socket = client_socket
            print('connected to raspberry by ' + str(client_address))
            client_raspberry_thread = threading.Thread(target=rasberry_handle, args=(client_raspberry_socket, ))
            client_raspberry_thread.daemon = True
            client_raspberry_thread.start()
            if unity_connect:
                cilent_unity_socket.send('OK'.encode())
    except socket.timeout:
        if raspberry_connect == False and unity_connect == True:
            cilent_unity_socket.send('Respberry Pi Connect Failed'.encode())
        continue



server_socket.close()

