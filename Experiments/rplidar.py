import time
# import VideoServiceClient as vsc
# import zmq
import cv2
import threading
import numpy as np
import atexit
import keyboard
from rplidar import RPLidar
import subprocess

class PromobotAPI:
    t = 0
    measurements = []
    process = None
    lidar_port = "COM5"

    def __init__(self, port='com3'):
        self.lidar_port = port


    def lidar_work(self):
        angle = 0
        index = 0
        self.measurements = []
        for i in range(15):
            self.measurements.append([])
        while self.process.poll() is None:
            try:
                data = str(self.process.stdout.readline().decode("utf-8").strip())
            except:
                print("Reading data error!")
                continue
            # print(data)
            angle_old = angle
            try:  # theta: 13.34 dist: 351.45 Q:47
                angle = float(data[(data.find(":") + 2):(data.find(".") + 3)])
                distance = float(data[(data.rfind(".") - 5):(data.rfind(".") + 3)])
                # print(angle, "  ", distance)
            except:
                print(data)
                print("Parsing data error!")
                continue
            if angle < angle_old:
                if len(self.measurements[len(self.measurements) - 1]) > index:
                    for i in range(index, len(self.measurements[len(self.measurements) - 1])):
                        self.measurements[len(self.measurements) - 1].pop()
                index = 0
                self.measurements.pop(0)
                self.measurements.append([])
            if index + 1 > len(self.measurements[len(self.measurements) - 1]):
                self.measurements[len(self.measurements) - 1].append((angle, distance))
            else:
                self.measurements[len(self.measurements) - 1][index] = (angle, distance)
            index += 1
        self.isLidarWorking = False

    def lidar_start(self):
        if self.lidar is not None:
            self.lidar.disconnect()
            self.lidar = None
            time.sleep(1)
        if not self.isLidarWorking:
            self.isLidarWorking = True
            self.process = subprocess.Popen("C:/Robot/ultra_simple.exe //./" + self.lidar_port,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            while self.process.poll() is not None:
                pass
            thread = threading.Thread(target=self.lidar_work)
            thread.daemon = True
            thread.start()

    def lidar_stop(self):
        if self.process.poll() is None:
            self.process.kill()
        while self.process.poll() is None:
            pass
        self.lidar = RPLidar(self.lidar_port)
        self.lidar.connect()
        self.lidar.stop_motor()
        self.lidar.stop()
