from BLE_GetSensorData import initializeSensor, getSensorData
from mpu6050_SensorData import initializeMPU6050, getAngle, calibration
import socket
import time
import json
import threading


SERVER_HOST = '192.168.100.166'
SERVER_PORT = 30000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_HOST, SERVER_PORT))

'''
SERVER_HOST_MPU = '192.168.100.166'
SERVER_PORT_MPU = 31000
s_mpu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_mpu.connect((SERVER_HOST_MPU, SERVER_PORT_MPU))
'''

device, bleData = initializeSensor()

data = {
    'speed': 0.0,
    'cadence': 0.0,
}

data_mpu = {
    'angle': 0.0,
}

# mpu 6050
def mpu():
    bus = initializeMPU6050()
    gyro_error = calibration(bus)
    while True:
        start = time.time()
        angle = getAngle(bus, gyro_error)
        end = time.time()
        data_mpu['angle'] = angle
        json_data = json.dumps(data_mpu)
        # print("mpu time: ", end - start)
        # print("Angle: ", angle)
        s.send(json_data.encode())

thread_mpu = threading.Thread(target = mpu)
thread_mpu.start()

# bluetooth
while True:
    start = time.time()
    if getSensorData(device):
        data['speed'] = bleData.speed
        data['cadence'] = bleData.cadence
        json_data = json.dumps(data)
        
        end = time.time()
        print("Speed: ", bleData.speed)
        print("Cadence: ", bleData.cadence)
        # print("bluetooth time: ", end - start)
        # print("----------------------")
        s.send(json_data.encode())
    else:
        break
    
print("Disconnected...")
s.close()
# s_mpu.close()