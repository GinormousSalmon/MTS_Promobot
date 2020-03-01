import MTSAPI as rapi
import time
import datetime
robot = rapi.RobotAPI(flag_serial=False)
# robot.set_camera_high_res()
# robot.beep()
# robot.blue()
print("Start RAW")
t = time.time()
c = 0
robot.manual_mode = 1
angle = 0
while 1:
    frame = robot.get_frame()  # .copy()

    # if robot.button()==1:========
    #     z = 0 / 0
    # print(robot.mouse_x, robot.mouse_y)
    # robot.wait(10)
    # if robot.vcc() < 9.5 and time.time()-t > 5:
    #     robot.beep()
    #     t = time.time()
    if time.time()-t > 1.05:
        t = time.time()
        # f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        # temp = int(f.readline()) / 1000
        # print(datetime.datetime.now(),temp)
        print(datetime.datetime.now())
    #
    #     c += 1
        # print(c)
        # print(time.time())
    #
    # m = robot.get_key()
    # if m == 113:
    #     cv2.imwrite("/home/pi/robot/dataset/screen"+str(time.time())+".jpg", frame)
    #     print("make screen")
    #
    # # if robot.manual(m) == 1:
    # #     continue
    # if m != -1:
    #     print(m)

    # if robot.joy_y != 0 or robot.joy_x != 0:
    #     robot.move(robot.joy_x+robot.joy_y, robot.joy_x-robot.joy_y)

    # для машинки
    # manual_speed = 250
    # if m == 38:
    #     robot.move(manual_speed, manual_speed, 100, True)
    # if m == 40:
    #     robot.move(-manual_speed, -manual_speed, 100, True)
    # if m == 39:
    #     angle = 30
    #     robot.servo(angle)
    # if m == 37:
    #     angle = -40
    #     robot.servo(angle)
    # if m == 32:
    #     angle = -10
    #     robot.servo(angle)

    # print(angle)

    # %^^&*
    # print(time.time())
    # frame = cv2.resize(frame, None, fx=0.25, fy=0.25)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame = robot.text_to_frame(frame, "raw: "+str(c), 30,30)

    robot.set_frame(frame, 20)
