import socket

HOST = '127.0.0.1'
PORT = 30000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

outdata = '30427_hd_Trim_Trim.mp4'
print('send: ' + outdata)
s.send(outdata.encode())

indata = s.recv(1024)
print('recv: ' + indata.decode())

s.close()