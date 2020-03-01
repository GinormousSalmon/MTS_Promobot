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
import speech_recognition as sr
import pyttsx3
import serial
from termcolor import colored


class PromobotAPI:
    port = None
    server_flag = False
    last_frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
    quality = 50
    manual_mode = 0
    manual_video = 1
    manual_speed = 150
    manual_angle_yaw = 70
    manual_angle_pitch = 70
    frame = []
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
    audio_queue = []
    thread_listening = None
    stop_listen = True
    recognizer = None
    text_queue = []
    flag_speech = True
    flag_tts = True
    flag_lidar = True
    voices = ["HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0",
              "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0",
              "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"]
    voice_engine = None
    tts_queue = []
    tts_work = False
    servo_yaw_angle = 0
    servo_pitch_angle = 0
    last_key = 0

    def __init__(self, flag_serial=True, flag_camera=True, flag_speech=True, flag_tts=True, flag_lidar=True,
                 voice_type=0):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        self.flag_camera = flag_camera
        self.flag_speech = flag_speech
        self.flag_serial = flag_serial
        self.flag_tts = flag_tts
        self.flag_lidar = flag_lidar
        print("Start script")
        if flag_tts:
            self.voice_engine = pyttsx3.init()
            self.voice_engine.setProperty('voice', self.voices[voice_type])
        if flag_speech:
            self.recognizer = sr.Recognizer()
        # print("open robot port")
        if flag_serial:
            self.port = serial.Serial('COM3', 500000, timeout=2)
            time.sleep(1.5)
            if self.send("CONNECT").__contains__("OK"):
                print(colored("Arduino connected", "green"))
            else:
                print(colored("Arduino connect error", "red"))
        if flag_camera:
            self.cap = cv2.VideoCapture()
            self.cap.open(0)
            r, self.frame = self.cap.read()
            self.time_frame = time.time()
        if self.flag_serial:
            self.servo_yaw(70)
            self.servo_pitch(70)
            if self.flag_lidar:
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
        self.move(0, 0)
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

    def get_frame(self):
        return self.rotate_image(self.frame, 180)

    @staticmethod
    def rotate_image(image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result

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
        if self.flag_lidar:
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

    def listening(self):
        while True:
            if len(self.audio_queue) > 0:
                try:
                    audio = self.audio_queue.pop()
                    print("Распознавание...")
                    t = time.time()
                    text = self.recognizer.recognize_google(audio, language="ru-RU")
                    self.text_queue.append(text)
                    print(self.recognizer.recognize_google(audio, language="ru-RU"))
                    print("Recognition time = ", time.time() - t)
                except sr.UnknownValueError:
                    print("Робот не расслышал фразу")
                    continue
                except sr.RequestError as e:
                    print("Ошибка сервиса; {0}".format(e))

    def start_listening(self):
        if self.flag_speech:
            if self.thread_listening is not None:
                if not self.thread_listening.isAlive():
                    self.stop_listen = False
                    self.thread_listening = threading.Thread(target=self.listening)
                    self.thread_listening.daemon = True
                    self.thread_listening.start()

    def stop_listening(self):
        if self.thread_listening is not None:
            if not self.thread_listening.isAlive():
                self.stop_listen = True

    def is_voice_command(self):
        return len(self.text_queue)

    def get_voice_command(self):
        if self.is_voice_command():
            return self.text_queue.pop()
        else:
            return -1

    def run_tts(self):
        self.voice_engine.runAndWait()

    def tts_working(self):
        self.tts_work = True
        print("working")
        while True:
            if len(self.tts_queue) > 0:
                if not self.voice_engine.isBusy():
                    text, wait = self.tts_queue.pop()
                    print("say")
                    self.voice_engine.say(text)
                    if wait:
                        self.voice_engine.runAndWait()
                    else:
                        thread = threading.Thread(target=self.run_tts)
                        thread.daemon = True
                        thread.start()
                else:
                    time.sleep(0.2)
            else:
                time.sleep(0.2)
        self.tts_work = False

    def say(self, text, wait=False):
        if self.flag_tts:
            print("start")
            self.tts_queue.append((text, wait))
            if not self.tts_work:
                self.tts_work = True
                thread = threading.Thread(target=self.tts_working)
                thread.daemon = True
                thread.start()

    def set_frame(self, frame):
        try:
            fps = int(100 / (time.time() - self.fps_timer)) / 100
        except ZeroDivisionError:
            fps = 500
        self.fps_timer = time.time()
        frame = self.text_to_frame(frame, str(fps), 0, 20, font_color=(0, 0, 255), font_size=1)
        cv2.imshow("frame", frame)
        self.k = cv2.waitKey(1)
        return

    @staticmethod
    def wait(millis):
        time.sleep(millis / 1000)

    def send(self, message, flag_wait=True):
        # print("send message")
        while self.port.in_waiting:
            self.port.readline()
        try:
            self.port.write(bytes(message.encode('utf-8')))
        except serial.SerialTimeoutException:
            print(colored("SerialTimeoutException", "red"))
        time.sleep(0.001)
        try:
            self.port.write(bytes("|\n".encode('utf-8')))
        except serial.SerialTimeoutException:
            print(colored("SerialTimeoutException"), "red")
        # time.sleep(0.01)
        answer = ""
        print("Sent " + message)
        if flag_wait:
            print("Waiting for answer...")
            while not self.port.in_waiting:
                pass
            # while self.port.in_waiting:
            answer = str(self.port.read_until(bytes('\n'.encode('utf-8'))))
            # answer = answer + str(self.port.readline())
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
            print("move waiting...")
            while not self.port.in_waiting:  # пока входной буфер пуст
                pass
            ans = ""
            # while self.port.in_waiting:
            # ans += str(self.port.readline())
            ans = str(self.port.read_until(bytes("\n".encode('utf-8'))))
            print("move_time end ", ans)
        # if wait:
        #     self.wait(time)
        return m

    def servo_yaw(self, angle, absolute=True):
        if absolute:
            self.servo_yaw_angle = angle
        else:
            self.servo_yaw_angle += angle
        self.servo_yaw_angle = self.constrain(self.servo_yaw_angle, 0, 180)
        return self.send("SERVO_YAW|" + str(self.servo_yaw_angle))

    def servo_pitch(self, angle, absolute=True):
        if absolute:
            self.servo_pitch_angle = angle
        else:
            self.servo_pitch_angle += angle
        self.servo_pitch_angle = self.constrain(self.servo_pitch_angle, 0, 180)
        return self.send("SERVO_PITCH|" + str(self.servo_pitch_angle))

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
        return self.text_to_frame(frame, str(self.distance), 550, 20)

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

    def manual(self):
        if self.flag_camera:
            frame = self.get_frame()
        if self.k == ord("m"):
            self.wait(150)
            if self.manual_mode == 0:
                print("manual on")
                self.manual_mode = 1
            else:
                print("manual off")
                self.move(0, 0)
                self.manual_mode = 0
        if self.manual_mode == 1:
            if self.k == ord('w'):
                self.move(self.manual_speed, self.manual_speed, 50, wait=False)
            elif self.k == ord('s'):
                self.move(-self.manual_speed, -self.manual_speed, 50, wait=False)
            elif self.k == ord('d'):
                self.move(self.manual_speed, -self.manual_speed, 50, wait=False)
            elif self.k == ord('a'):
                self.move(-self.manual_speed, self.manual_speed, 50, wait=False)
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
                #     if self.k == ord('w'):
                #         self.move(self.manual_speed, self.manual_speed, 100, wait=True)
                #     elif self.k == ord('s'):
                #         self.move(-self.manual_speed, -self.manual_speed, 100, wait=True)
                #     elif self.k == ord('d'):
                #         self.move(self.manual_speed, -self.manual_speed, 100, wait=True)
                #     elif self.k == ord('a'):
                #         self.move(-self.manual_speed, self.manual_speed, 100, wait=True)
                # elif self.last_key == ord('w') or self.last_key == ord('a')\
                #         or self.last_key == ord('s') or self.last_key == ord('d'):
                #     self.move(0, 0, wait=True)
                # 75 72 77 80
                if keyboard.is_pressed("RIGHT"):
                    print("75")
                    self.servo_yaw(-10, absolute=False)
                if keyboard.is_pressed("LEFT"):
                    print("72")
                    self.servo_yaw(10, absolute=False)
                if keyboard.is_pressed("UP"):
                    print("77")
                    self.servo_pitch(-10, absolute=False)
                if keyboard.is_pressed("DOWN"):
                    print("80")
                    self.servo_pitch(10, absolute=False)
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
                self.last_key = self.k

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
