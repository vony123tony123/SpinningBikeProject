import socket
import time

HOST = '127.0.0.1'
Connect_PORT = 30000

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, Connect_PORT))
    outdata = '10 15 -45.5'
    while True:
        print('send: ' + outdata)
        s.send(outdata.encode())
        time.sleep(10)

except Exception as e:
    print(e)
    pass

s.close()