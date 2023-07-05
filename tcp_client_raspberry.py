import socket
import time
import json
HOST = '127.0.0.1'
Connect_PORT = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, Connect_PORT))

outdata = {
    "speed": 10.0,
    "cadence": 15.0,
    "angle": 15.0
}
connected_msg = "OK"
try:
    s.send(connected_msg.encode())
    time.sleep(5)
    while True:
        if outdata['angle'] == 15.0:
            outdata['angle'] = -15.0
            data = json.dumps(outdata)
            s.send(data.encode())
        elif outdata['angle'] == -15.0:
            outdata['angle'] = 15.0
            data = json.dumps(outdata)
            s.send(data.encode())
        print(outdata)
        time.sleep(5)

except Exception as e:
    print(e)
    pass

s.close()