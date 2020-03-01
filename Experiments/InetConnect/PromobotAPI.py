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
    port = None
    server_flag = False
    last_key = -1
    last_frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
    quality = 50
    manual_mode = 0
    manual_video = 1
    manual_speed = 150
    manual_angle_yaw = 70
    manual_angle_pitch = 70
    frame = []
    mouse_x = -1
    mouse_y = -1
    joy_x = 0
    joy_y = 0
    small_frame = 0
    motor_left = 0
    motor_right = 0
    encode_param = 0
    flag_serial = False
    flag_camera = False
    t = 0
    measurements = []
    process = None
    lidar_port = "COM5"
    lidar = None
    isLidarWorking = False
    k = 0
    fps_timer = 0

    def __init__(self, flag_serial=True, flag_camera=True):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        self.flag_camera = flag_camera
        self.flag_serial = flag_serial
        print("Start script")
        atexit.register(self.cleanup)
        # print("open robot port")
        if flag_serial:
            import serial
            self.port = serial.Serial('COM3', 2000000, timeout=2)
            time.sleep(1.5)
            print("Arduino connected")
        # vsc.VideoClient.inst().subscribe("ipc")
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break
        if flag_camera:
            self.cap = cv2.VideoCapture()
            self.cap.open(0)
            r, self.frame = self.cap.read()
            self.time_frame = time.time()
        # self.cap.set(cv2.CAP_PROP_FPS, 30)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.open(0)
        # if camera_high_res:
        #     self.set_camera_high_res()

        # if flag_video:
        #     self.context = zmq.Context(1)
        #     self.socket = self.context.socket(zmq.REP)
        #
        #     self.socket.bind("tcp://*:5555")
        #     # print("start video server")
        #     self.server_flag = True
        #     self.my_thread_video = threading.Thread(target=self.send_frame)
        #     self.my_thread_video.daemon = True
        #
        #     self.my_thread_video.start()

        # if flag_keyboard:
        #     # self.context2 = zmq.Context(1)
        #     # self.socket2 = self.context2.socket(zmq.REP)
        #     #
        #     # self.socket2.bind("tcp://*:5559")
        #     # # print("start video server")
        #     # self.server_keyboard = True
        #     self.my_thread = threading.Thread(target=self.receive_key)
        #     self.my_thread.daemon = True
        #     self.my_thread.start()

        # серву выставляем в нуль

        # if self.flag_serial:
        # self.servo(0)
        # очищаем буфер кнопки( если была нажата, то сбрасываем)
        # self.button()
        # выключаем все светодиоды
        if self.flag_serial:
            self.servo_yaw(70)
            self.servo_pitch(70)
            self.lidar_start()
            self.lidar_stop()
        self.stop_frames = False
        if flag_camera:
            self.my_thread_f = threading.Thread(target=self.work_f)
            self.my_thread_f.daemon = True
            self.my_thread_f.start()

        self.manual_video = 1
        pass

    def end_work(self):
        # self.cap.release()
        self.stop_frames = True
        self.wait(300)
        self.frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
        self.wait(1000)
        print("STOPPED ")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_work()

    def cleanup(self):
        self.end_work()
        # self.cap.release()

    def set_camera(self, fps=60, width=640, height=480):
        self.stop_frames = True
        self.wait(500)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.wait(500)
        self.stop_frames = False

    def set_camera_high_res(self):
        self.set_camera(30, 1024, 720)

    def set_camera_low_res(self):
        self.set_camera(60, 320, 240)

    def work_f(self):
        self.stop_frames = False
        while True:
            if not self.stop_frames:
                ret, frame = self.cap.read()
                if ret:
                    self.frame = frame
                    self.time_frame = time.time()
                    # time.sleep(0.001)

                    # self.wait(1)
            else:
                time.sleep(0.01)
        pass

    def get_key(self, clear=True):
        last = self.last_key
        self.last_key = -1
        return last

    def get_frame(self):
        return self.frame

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

    def set_frame(self, frame):
        fps = int(100 / (time.time() - self.fps_timer)) / 100
        frame = self.text_to_frame(frame, str(fps), 0, 20, font_color=(0, 0, 255), font_size=1)
        cv2.imshow("frame", frame)
        self.k = cv2.waitKey(1)
        self.fps_timer = time.time()
        return

    @staticmethod
    def wait(millis):
        time.sleep(millis / 1000)

    def send(self, message, flag_wait=True):
        # print("send message")
        self.port.write(bytes(message.encode('utf-8')))
        self.port.write(bytes("|\n".encode('utf-8')))
        # time.sleep(0.01)
        answer = ""
        print("Sent " + message)
        if flag_wait:
            print("Waiting for answer...")
            while not self.port.in_waiting:
                pass
            while self.port.in_waiting:
                answer = answer + str(self.port.readline())
            print("Got answer: " + answer[2:len(answer) - 5])
            return answer[2:len(answer) - 5]  # удаляем \r\n

    def move(self, m1, m2, time=0, encoder=0, wait=False):
        m1 = self.constrain(m1, -255, 255)
        m2 = self.constrain(m2, -255, 255)
        self.motor_left = m1
        self.motor_right = m2
        if time != 0:
            message = "MOVE_TIME|" + str(m1) + "|" + str(m2) + "|" + str(time)
        elif encoder != 0:
            message = "MOVE_ENCODER|" + str(m1) + "|" + str(m2) + "|" + str(encoder)
        else:
            message = "MOVE|" + str(m1) + "|" + str(m2)
        if wait:
            message += "|WAIT"
        print(message)
        m = self.send(message)
        if wait and (time != 0 or encoder != 0):
            while not self.port.in_waiting:  # пока входной буфер пуст
                pass
        # if wait:
        #     self.wait(time)
        return m

    def servo_yaw(self, angle):
        angle = self.constrain(angle, -180, 180)
        return self.send("SERVO_YAW|" + str(angle))

    def servo_pitch(self, angle):
        angle = self.constrain(angle, -180, 180)
        return self.send("SERVO_PITCH|" + str(angle))

    def distance(self):
        s = self.send("DISTANCE")
        s = s.split("|")
        d = -1
        try:
            d = float(s[1])
        except:
            pass
        return d

    def voltage(self):
        s = self.send("VOLTAGE")
        # pos = s.find("VCC")
        # s = s[pos:]
        s = s.split("|")
        v = -1
        try:
            v = float(s[1])
        except:
            pass
        return v

    @staticmethod
    def millis():
        return int(round(time.time() * 1000))

    @staticmethod
    def text_to_frame(frame, text, x, y, font_color=(255, 255, 255), font_size=2):
        cv2.putText(frame, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, font_color, font_size)
        return frame

    def vcc_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.voltage()), 10, 20)

    def dist_to_frame(self, frame):
        return self.text_to_frame(frame, str(self.distance()), 550, 20)

    @staticmethod
    def distance_between_points(xa, ya, xb, yb, za=0, zb=0):
        return np.sqrt(np.sum((np.array((xa, ya, za)) - np.array((xb, yb, zb))) ** 2))

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    @staticmethod
    def constrain(x, min, max):
        if x < min:
            return min
        else:
            if x > max:
                return max
            else:
                return x

    def manual(self, c=-1, show_code=False):
        # m = c
        # if c == -1:
        #     m = self.get_key()
        # if self.flag_camera:
        #     frame = self.get_frame()
        # if keyboard.is_pressed("m"):
        #     self.wait(200)
        #     if self.manual_mode == 0:
        #         print("manual on")
        #         self.manual_mode = 1
        #     else:
        #         print("manual off")
        #         self.manual_mode = 0
        # if time.time() - self.t > 0.1:
        #     self.t = time.time()
        #     if keyboard.is_pressed('1'):
        #         if self.small_frame == 1:
        #             self.small_frame = 0
        #         else:
        #             self.small_frame = 1
        #
        #     if self.manual_mode == 0:
        #         return self.manual_mode
        #
        #     if self.manual_mode == 1:
        #         if keyboard.is_pressed('w'):
        #             self.move(self.manual_speed, self.manual_speed, wait=True)
        #         elif keyboard.is_pressed('s'):
        #             self.move(-self.manual_speed, -self.manual_speed, wait=True)
        #         elif keyboard.is_pressed('d'):
        #             self.move(self.manual_speed, -self.manual_speed, wait=True)
        #         elif keyboard.is_pressed('a'):
        #             self.move(-self.manual_speed, self.manual_speed, wait=True)
        #         else:
        #             self.move(0, 0, wait=True)
        #         # 75 72 77 80
        #         if keyboard.is_pressed("RIGHT"):
        #             print("75")
        #             self.manual_angle_yaw -= 10
        #             self.manual_angle_yaw = self.constrain(self.manual_angle_yaw, 0, 90)
        #             self.servo_yaw(self.manual_angle_yaw)
        #         if keyboard.is_pressed("LEFT"):
        #             print("72")
        #             self.manual_angle_yaw += 10
        #             self.manual_angle_yaw = self.constrain(self.manual_angle_yaw, 0, 90)
        #             self.servo_yaw(self.manual_angle_yaw)
        #         if keyboard.is_pressed("UP"):
        #             print("77")
        #             self.manual_angle_pitch -= 10
        #             self.manual_angle_pitch = self.constrain(self.manual_angle_pitch, 0, 90)
        #             self.servo_pitch(self.manual_angle_pitch)
        #         if keyboard.is_pressed("DOWN"):
        #             print("80")
        #             self.manual_angle_pitch += 10
        #             self.manual_angle_pitch = self.constrain(self.manual_angle_pitch, 0, 90)
        #             self.servo_pitch(self.manual_angle_pitch)
        #         if keyboard.is_pressed(' '):
        #             print("' '")
        #             self.manual_angle_pitch = 70
        #             self.manual_angle_yaw = 70
        #             self.servo_yaw(self.manual_angle_yaw)
        #             self.servo_pitch(self.manual_angle_pitch)
        #         if keyboard.is_pressed('-'):
        #             self.manual_speed -= 20
        #             if self.manual_speed < 50:
        #                 self.manual_speed = 50
        #
        #         if keyboard.is_pressed('+'):
        #             self.manual_speed += 20
        #             if self.manual_speed > 250:
        #                 self.manual_speed = 250
        #
        #         if keyboard.is_pressed('0'):
        #             if self.manual_video == 0:
        #                 self.manual_video = 1
        #             else:
        #                 self.manual_video = 0

        if self.flag_camera:
            frame = self.get_frame()
        if self.k == ord("m"):
            self.wait(200)
            if self.manual_mode == 0:
                print("manual on")
                self.manual_mode = 1
            else:
                print("manual off")
                self.manual_mode = 0
        if time.time() - self.t > 0.1:
            self.t = time.time()
            if self.k == ord('1'):
                if self.small_frame == 1:
                    self.small_frame = 0
                else:
                    self.small_frame = 1

            if self.manual_mode == 0:
                return self.manual_mode

            if self.manual_mode == 1:
                if self.k == ord('w'):
                    self.move(self.manual_speed, self.manual_speed, wait=True)
                elif self.k == ord('s'):
                    self.move(-self.manual_speed, -self.manual_speed, wait=True)
                elif self.k == ord('d'):
                    self.move(self.manual_speed, -self.manual_speed, wait=True)
                elif self.k == ord('a'):
                    self.move(-self.manual_speed, self.manual_speed, wait=True)
                else:
                    self.move(0, 0, wait=True)
                # 75 72 77 80
                if keyboard.is_pressed("RIGHT"):
                    print("75")
                    self.manual_angle_yaw -= 10
                    self.manual_angle_yaw = self.constrain(self.manual_angle_yaw, 0, 90)
                    self.servo_yaw(self.manual_angle_yaw)
                if keyboard.is_pressed("LEFT"):
                    print("72")
                    self.manual_angle_yaw += 10
                    self.manual_angle_yaw = self.constrain(self.manual_angle_yaw, 0, 90)
                    self.servo_yaw(self.manual_angle_yaw)
                if keyboard.is_pressed("UP"):
                    print("77")
                    self.manual_angle_pitch -= 10
                    self.manual_angle_pitch = self.constrain(self.manual_angle_pitch, 0, 90)
                    self.servo_pitch(self.manual_angle_pitch)
                if keyboard.is_pressed("DOWN"):
                    print("80")
                    self.manual_angle_pitch += 10
                    self.manual_angle_pitch = self.constrain(self.manual_angle_pitch, 0, 90)
                    self.servo_pitch(self.manual_angle_pitch)
                if self.k == ord(' '):
                    print("' '")
                    self.manual_angle_pitch = 70
                    self.manual_angle_yaw = 70
                    self.servo_yaw(self.manual_angle_yaw)
                    self.servo_pitch(self.manual_angle_pitch)
                if self.k == ord('-'):
                    self.manual_speed -= 20
                    if self.manual_speed < 50:
                        self.manual_speed = 50

                if self.k == ord('+'):
                    self.manual_speed += 20
                    if self.manual_speed > 250:
                        self.manual_speed = 250

                if self.k == ord('0'):
                    if self.manual_video == 0:
                        self.manual_video = 1
                    else:
                        self.manual_video = 0

                #     self.set_frame(
                # self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20))))

        if self.manual_mode == 1 and self.flag_camera == 1:
            if self.small_frame == 1:
                frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
                self.set_frame(frame)
                return self.manual_mode

            # frame = self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(
            #    self.text_to_frame(frame, str(self.manual_speed), 0, 100), "manual", 280, 20)))
            frame = self.text_to_frame(self.text_to_frame(frame, "manual", 280, 20), str(self.manual_speed), 0, 100)
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.set_frame(frame)

        return self.manual_mode
