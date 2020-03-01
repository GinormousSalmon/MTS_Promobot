import time
# import VideoServiceClient as vsc
import zmq
import cv2
import threading
import numpy as np
import atexit


class RobotAPI:
    port = None
    server_flag = False
    last_key = -1
    last_frame = np.array([[10, 10], [10, 10]], dtype=np.uint8)
    quality = 50
    manual_mode = 0
    manual_video = 1
    manual_speed = 150
    manual_angle = 0
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

    def __init__(self, flag_video=True, flag_keyboard=True, flag_serial=True):
        # print("\x1b[42m" + "Start script" + "\x1b[0m")
        self.flag_serial = flag_serial
        print("Start script")
        atexit.register(self.cleanup)
        # print("open robot port")
        if flag_serial:
            import serial
            self.port = serial.Serial('COM11', 2000000, timeout=2)
            time.sleep(0.5)
        # vsc.VideoClient.inst().subscribe("ipc")
        # vsc.VideoClient.inst().subscribe("tcp://127.0.0.1")
        # vsc.VideoClient.inst().subscribe("udp://127.0.0.1")

        # while True:
        #     frame = vsc.VideoClient.inst().get_frame()
        #     if frame.size != 4:
        #         break
        self.cap = cv2.VideoCapture()
        self.cap.open(0)
        # self.cap.set(cv2.CAP_PROP_FPS, 30)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.open(0)
        # if camera_high_res:
        #     self.set_camera_high_res()
        r, self.frame = self.cap.read()
        self.time_frame = time.time()

        if flag_video:
            self.context = zmq.Context(1)
            self.socket = self.context.socket(zmq.REP)

            self.socket.bind("tcp://*:5555")
            # print("start video server")
            self.server_flag = True
            self.my_thread_video = threading.Thread(target=self.send_frame)
            self.my_thread_video.daemon = True

            self.my_thread_video.start()

        if flag_keyboard:
            self.context2 = zmq.Context(1)
            self.socket2 = self.context2.socket(zmq.REP)

            self.socket2.bind("tcp://*:5559")
            # print("start video server")
            self.server_keyboard = True
            self.my_thread = threading.Thread(target=self.receive_key)
            self.my_thread.daemon = True
            self.my_thread.start()

        # серву выставляем в нуль

        if self.flag_serial:
            self.servo(0)
            # очищаем буфер кнопки( если была нажата, то сбрасываем)
            # self.button()
            # выключаем все светодиоды
        self.stop_frames = False
        self.my_thread_f = threading.Thread(target=self.work_f)
        self.my_thread_f.daemon = True
        self.my_thread_f.start()

        self.manual_video = 1
        pass

    def end_work(self):
        # self.cap.release()
        if self.flag_serial:
            self.servo(0)
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

    def receive_key(self):
        while True:
            message = ""
            try:

                message = self.socket2.recv_string()
            except:
                pass
            if message.find("m") > -1:
                message = message.split(",")
                self.mouse_x = int(message[1])
                self.mouse_y = int(message[2])
                # print(message)
            elif message.find("j") > -1:
                message = message.split(",")
                self.joy_x = float(message[1])
                self.joy_y = float(message[2])

            else:
                self.last_key = int(message.lstrip())
            try:
                self.socket2.send_string("1")
            except:
                pass
            # print(self.last_key)
            # self.wait(10)
        pass

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

    def send_frame(self):
        while True:
            if self.last_frame is not None:
                if self.server_flag and self.last_frame.shape[0] > 2:
                    message = ""
                    try:
                        message = self.socket.recv_string()
                    except:
                        pass

                    if message == "1":
                        try:
                            self.encode_param = [int(cv2.IMWRITE_JPEG_LUMA_QUALITY), self.quality]
                            result, frame = cv2.imencode('.jpg', self.last_frame, self.encode_param)

                            md = dict(
                                dtype=str(frame.dtype),
                                shape=frame.shape,
                            )

                            self.socket.send_json(md, zmq.SNDMORE)
                            self.socket.send(frame, 0)

                        except:
                            pass
                else:
                    try:
                        self.socket.send_string("0")
                    except:
                        pass

                # self.wait(10)
                continue

    def set_frame(self, frame, quality=30):
        self.quality = quality
        self.last_frame = frame
        return

    @staticmethod
    def wait(t):
        # print(t/1000)
        time.sleep(t / 1000)

    def send(self, message, flag_wait=True):
        # print("send message")
        self.port.write(bytes(message.encode('utf-8')))
        self.port.write(bytes("\n".encode('utf-8')))
        # time.sleep(0.01)
        answer = ""
        if flag_wait:
            while not self.port.in_waiting:
                pass
            while self.port.in_waiting:
                answer = answer + str(self.port.readline())
            return answer[2:len(answer) - 5]  # удаляем \r\n

    def move(self, m1, m2, time, wait=False):
        m1 = self.constrain(m1, -255, 255)
        m2 = self.constrain(m2, -255, 255)
        self.motor_left = m1
        self.motor_right = m2
        m = self.send("MOVE," + str(m1) + "," + str(m2) + "," + str(time))
        if wait:
            self.wait(time)
        return m

    def servo(self, angle):
        angle = self.constrain(angle, -180, 180)
        return self.send("SERVO," + str(angle))

    def distance(self):
        s = self.send("DISTANCE")
        s = s.split(",")
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
        s = s.split(",")
        v = -1
        try:
            v = float(s[1])
        except:
            pass
        return v

    def step(self, motorL, motorR, time_step=20, pulse_go=10, pause_go=20, pulse_stop=5, pause_stop=3, wait=True):
        motorL = self.constrain(motorL, -255, 255)
        motorR = self.constrain(motorR, -255, 255)
        self.motor_left = motorL
        self.motor_right = motorR

        m = self.send("STEP," + str(motorL) + "," + str(motorR) + "," + str(pulse_go) + "," + str(pause_go) + "," + str(
            pulse_stop) + "," + str(pause_stop) + "," + str(time_step))
        # print(m)
        if wait:
            self.wait(time_step)
        # self.move(motorL, motorR, pulse_go)
        # self.wait(pause_go)
        # self.move(-motorL, -motorR, pulse_stop)
        # self.wait(pause_stop)
        return m

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
        m = c
        if c == -1:
            m = self.get_key()
        frame = self.get_frame()

        if m == ord('m') or m == ord('ь'):
            if self.manual_mode == 0:
                print("manual on")
                self.manual_mode = 1
            else:
                print("manual off")
                self.manual_mode = 0
        if m == ord('1'):
            if self.small_frame == 1:
                self.small_frame = 0
            else:
                self.small_frame = 1

        if self.manual_mode == 0:
            return self.manual_mode

        if m > -1 and self.manual_mode == 1:

            if m == ord('w') or m == ord('ц'):
                self.move(self.manual_speed, self.manual_speed, 50, True)
            if m == ord('s') or m == ord('ы'):
                self.move(-self.manual_speed, -self.manual_speed, 50, True)
            if m == ord('d') or m == ord('в'):
                self.move(self.manual_speed, -self.manual_speed, 50, True)
            if m == ord('a') or m == ord('ф'):
                self.move(-self.manual_speed, self.manual_speed, 50, True)
            if m == ord('<') or m == ord('б'):
                self.manual_angle -= 30
                self.servo(self.manual_angle)
            if m == ord('>') or m == ord('ю'):
                self.manual_angle += 30
                self.servo(self.manual_angle)
            if m == ord(' '):
                self.manual_angle = 0
                self.servo(self.manual_angle)
            if m == ord('-'):
                self.manual_speed -= 20
                if self.manual_speed < 50:
                    self.manual_speed = 50

            if m == ord('+'):
                self.manual_speed += 20
                if self.manual_speed > 250:
                    self.manual_speed = 250

            if m == 86:
                if self.manual_video == 0:
                    self.manual_video = 1
                else:
                    self.manual_video = 0
            if show_code:
                print(m)

                #     self.set_frame(
                # self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(frame, "manual", 280, 20))))

        if self.manual_mode == 1 and self.manual_video == 1:
            if self.small_frame == 1:
                frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
                self.set_frame(frame, 10)
                return self.manual_mode

            frame = self.dist_to_frame(self.vcc_to_frame(self.text_to_frame(
                self.text_to_frame(frame, str(self.manual_speed), 0, 100), "manual", 280, 20)))
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.set_frame(frame)

        return self.manual_mode
