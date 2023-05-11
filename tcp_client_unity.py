import socket
import random

HOST = '127.0.0.1'
PORT = 14786
Connect_PORT = 30000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.connect((HOST, Connect_PORT))
s.settimeout(1)

while True:
    try:
        indata = s.recv(1024)
        print('recv: ' + indata.decode())

        if random.random() > 0.5:
            print('***********')
            outdata = '30427_hd_Trim_Trim.mp4'
            print('send: ' + outdata)
            s.send(outdata.encode())
            print("*****************")

    except socket.timeout:
        continue

s.close()