import os
import socket as sc
import threading
import time
import tkinter.filedialog as tkFileDialog
import tkinter as tk

import cv2
import numpy as np
import zmq
import zlib
import base64

import InetConnection as InetConnection

MOUSE_FLAG = False
if MOUSE_FLAG:
    import mouse

JOYSTICK_FLAG = True
if JOYSTICK_FLAG:
    import pygame

    pygame.init()
    pygame.joystick.init()

# FRAME = np.ndarray(shape=(240, 320, 3), dtype=np.uint8)
FRAME = 0
DATASET = False

if DATASET:
    import pickle

# ic = InetConnection.InetConnect(sc.gethostname(), "client")
# ic.take_list()


Reset = "\x1b[0m"
Bright = "\x1b[1m"
Dim = "\x1b[2m"
Underscore = "\x1b[4m"
Blink = "\x1b[5m"
Reverse = "\x1b[7m"
Hidden = "\x1b[8m"

FgBlack = "\x1b[30m"
FgRed = "\x1b[31m"
FgGreen = "\x1b[32m"
FgYellow = "\x1b[33m"
FgBlue = "\x1b[34m"
FgMagenta = "\x1b[35m"
FgCyan = "\x1b[36m"
FgWhite = "\x1b[37m"

BgBlack = "\x1b[40m"
BgRed = "\x1b[41m"
BgGreen = "\x1b[42m"
BgYellow = "\x1b[43m"
BgBlue = "\x1b[44m"
BgMagenta = "\x1b[45m"
BgCyan = "\x1b[46m"
BgWhite = "\x1b[47m"

flag_internet_work = False

port = "5557"

list_combobox = []
robot_address = "-1"
robot_address_internet = "-1"

# vd = vsc.VideoClient().inst()
# socket.connect ("tcp://192.168.88.19:%s" % port)


selected_file = ""
selected_file_no_dir = ""
video_show = 0
video_show2 = 3
video_show2_global = 0
video_show_work = False
started_flag = 0
receive_flag = 0
key_started = -1
key_pressed = 0
mouse_x = -1
mouse_y = -1
fps_show = 1
fps = 0
socket_2_connected = False
joy_x = 0
joy_y = 0
key_pressed_dataset = 0
flag_sent_file = False


def camera_work():
    global root, video_show2, socket2, video_show2_global, image, started_flag, flag_internet_work, \
        socket_2_connected, DATASET, FRAME, fps
    ic_v = InetConnection.InetConnect(sc.gethostname() + "_v", "client")
    ic_v.connect()
    image = np.zeros((480, 640, 3), np.uint8)
    time_frame = time.time()
    frames = 0
    frames_time = time.time()

    while 1:
        # try:
        # print("s",started_flag)
        # print("video status", video_show2_global, video_show2)
        if video_show2_global == 1:
            if video_show2 == 1:  # and started_flag == 1:
                # print("vid1", flag_internet_work)
                if flag_internet_work:
                    ic_v.send_and_wait_answer(robot_address_internet, "p_MTS")
                    while 1:
                        j_mesg, jpg_bytes = ic_v.take_answer_bytes()
                        if len(jpg_bytes) > 1:
                            try:
                                A = np.frombuffer(jpg_bytes, dtype=j_mesg['dtype'])
                                image = A.reshape(j_mesg['shape'])
                                image = cv2.imdecode(image, 1)
                                time_frame = time.time()
                                frames += 1

                            except:
                                pass

                        else:
                            # time.sleep(0.01)
                            break
                            # continue
                else:

                    try:
                        socket2.send_string("1", zmq.NOBLOCK)  # zmq.NOBLOCK
                    except:
                        # print("error", e)
                        pass
                    md = ""
                    t = time.time()
                    while 1:
                        try:
                            md = socket2.recv_json(zmq.NOBLOCK)
                        except:
                            pass
                        if md != "":
                            break
                        if time.time() - t > 1:
                            # print("break video")
                            break

                    if md != "" and video_show2 == 1:
                        msg = 0
                        t = time.time()
                        while 1:
                            try:
                                msg = socket2.recv(zmq.NOBLOCK)
                            except:
                                pass
                                # print("error", e)
                            if msg != 0:
                                break
                            if time.time() - t > 1:
                                # print("break video")
                                break

                        try:

                            A = np.frombuffer(msg, dtype=md['dtype'])
                            image = A.reshape(md['shape'])
                            image = cv2.imdecode(image, 1)
                            time_frame = time.time()
                            # print("frame", md['shape'])
                            # cv2.imshow("Robot frame", image)
                            # cv2.waitKey(1)
                            frames += 1
                            if DATASET:
                                FRAME = image.copy()

                        except:
                            pass

                # отрисовываем картинку
                if time.time() - time_frame > 2:

                    cv2.putText(image, "video lost", (10, int(image.shape[0] - 10)), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                (255, 255, 255))
                    for i in range(int(time.time() - time_frame)):
                        cv2.putText(image, ".", (140 + (i * 10), int(image.shape[0] - 10)),
                                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                    (255, 255, 255))

                    # автореконнект видео
                    if time.time() - time_frame > 5:
                        # print("reconnect video")
                        if flag_internet_work:
                            ic_v.disconnect()

                        else:
                            if socket_2_connected:
                                socket2.close()

                        time_frame = time.time()
                        video_show2 = 0

                        continue

                if frames_time < time.time():
                    fps = frames
                    # print("fps:",fps)
                    frames_time = int(time.time()) + 1
                    # print(frames_time)
                    frames = 0
                if fps_show == 1:
                    cv2.putText(image, "fps:" + str(fps), (int(image.shape[1] - 80), int(image.shape[0] - 10)),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                (255, 255, 255))
                cv2.imshow("Robot frame", image)
                FRAME = image.copy()

                cv2.waitKey(1)
                continue

            if video_show2 == 0:

                if flag_internet_work:
                    video_show2 = 1
                    ic_v.connect()
                    continue
                else:
                    # print("Connecting to soft...", robot_address)
                    cv2.destroyAllWindows()
                    for i in range(1, 5):
                        cv2.waitKey(1)
                    context = zmq.Context()
                    socket2 = context.socket(zmq.REQ)
                    socket2.connect("tcp://" + robot_address + ":5555")
                    socket_2_connected = True
                    pass

                image = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(image, "Connect to robot...", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                time_frame = time.time()
                video_show2 = 1
                cv2.namedWindow("Robot frame")
                cv2.startWindowThread()
                # print("connected")

                continue
            if video_show2 == -1:
                # print("vid-1")
                # print("close socket2")

                cv2.destroyAllWindows()
                for i in range(1, 5):
                    cv2.waitKey(1)

                if flag_internet_work:
                    video_show2 = 3
                    continue

                if socket_2_connected:
                    socket2.close()
                    socket_2_connected = False

                time.sleep(0.1)
                video_show2 = 3
                ic_v.disconnect()
                time.sleep(0.05)
                # print("video_show2", video_show2 )

                continue
            if video_show2 == 3:
                # print("vid3")
                # cv2.imshow("Robot frame", image)
                # cv2.destroyWindow("Robot frame")
                cv2.destroyAllWindows()
                for i in range(1, 5):
                    cv2.waitKey(1)

                time.sleep(0.05)
                continue
                # print("vid??", video_show2, "started_flag==", started_flag)

        else:

            cv2.destroyAllWindows()
            cv2.waitKey(1)
            video_show2 = 3
            time.sleep(0.1)
            # except:
            #     print("error video")
            #     pass


my_thread = threading.Thread(target=camera_work)
my_thread.daemon = True
my_thread.start()

ic = InetConnection.InetConnect(sc.gethostname() + "_r", "client")
ic.connect()


def robot_receive_work():
    global video_show2, receive_flag, started_flag, flag_internet_work, ic, selected_file_no_dir, \
        selected_file, robot_address, flag_sent_file
    color_log = FgBlack
    # ic = InetConnection.InetConnect(sc.gethostname() + "_r", "client")
    # ic.connect()
    time_receive = time.time()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    while 1:
        # try:
        # if receive_flag != 0:
        # print("receive_flag", receive_flag)
        time.sleep(0.1)
        if receive_flag == 1:
            message_s = ""
            if flag_internet_work:
                message_s = ic.send_and_wait_answer(robot_address_internet, "d_MTS")
                time_receive = time.time()
                pass
            else:
                # try:
                #     #print("send..")
                #     socket.send_string("data")
                #     message_s = str(socket.recv_string())
                #     #print("receive ok")
                # except:
                #     pass

                t = time.time()
                while 1:
                    f = 0
                    try:
                        socket.send_string("data", zmq.NOBLOCK)  # zmq.NOBLOCK
                        f = 1
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            # print("error", e)
                            pass
                    if f == 1:
                        break
                    if time.time() - t > 1:
                        break
                message_s = ""
                t = time.time()
                while 1:
                    f = 0
                    try:
                        message_s = socket.recv_string(zmq.NOBLOCK)
                        time_receive = time.time()
                        f = 1
                    except zmq.ZMQError as e:
                        if e.errno == zmq.ETERM:
                            pass
                            # print("error", e)
                    if message_s != "" or f == 1:
                        break

                    if time.time() - t > 1:
                        break
            # print(message_s.encode('utf-8'))
            # message_s=message_s.replace("/n", "")

            if message_s is None:
                time.sleep(0.01)
                continue

            if time.time() - time_receive > 10:
                print("lost connect ..", time.time() - time_receive)
                printt("lost connect ..", str(time.time() - time_receive))
                if flag_internet_work:
                    ic.disconnect()
                    ic.connect()
                    pass
                else:
                    time_receive = time.time()
                    socket.close()
                    socket = context.socket(zmq.REQ)
                    socket.connect("tcp://" + robot_address + ":%s" % port)
                    socket.send_string("take|" + robot_address)
                    otvet = socket.recv_string()
                    print("Connected to robot: " + BgGreen + otvet + Reset)
                    printt("Connected to robot: " + otvet, fg='white', bg='green')
                print("reconnected")
                printt("reconnected")
                if started_flag:
                    receive_flag = 1
                else:
                    receive_flag = 0

            # if message_s.find("stoping") >= 0:
            #     receive_flag=-1

            if message_s.find("STOPPED") >= 0:
                receive_flag = 0
                if started_flag == 1:
                    printt(message_s, fg='red')
                    message_s = message_s.replace("STOPPED", FgRed + "STOPPED" + Reset)
                    print(color_log + message_s.rstrip())

                # print("reciv1_stope")
                # message_s = ""
                # video_show2 = -1
                color_log = FgBlack

                # if video_show2 != 3:
                #     video_show2 = -1
                video_show2 = -1
                time.sleep(0.01)
                # while video_show2 != 3 or video_show2 != 0:
                #     print("stop_wideo", video_show2 )
                #     time.sleep(0.3)

                # cv2.destroyAllWindows()
                # kill_windows()

                started_flag = 0
                # if flag_internet_work:
                #     ic.clear()
                time.sleep(0.01)
                continue

            if message_s != "" and len(message_s) > 0:
                # обрезаем конец сообщения, спец символ
                fg = 'black'
                if message_s.find("Traceback") >= 0 or message_s.find("Error:") >= 0:
                    color_log = FgRed
                    video_show2 = -1
                    fg = 'red'

                print(color_log + message_s.rstrip())
                printt(message_s.rstrip(), fg)

            time.sleep(0.01)

        if receive_flag == -1:
            color_log = FgBlack
            ret = ""
            if flag_internet_work:
                ret = ic.send_and_wait_answer(robot_address_internet, "stop_MTS")
                ic.send_and_wait_answer(robot_address_internet, "stopvideo_MTS")
                pass
            else:
                try:
                    socket.send_string("stop_MTS")
                    ret = socket.recv_string()
                except:
                    pass
            # if started_flag == 1:
            #     print(ret.replace("STOPPED", FgRed + "STOPPED" + Reset))
            # receive_flag = 0
            receive_flag = 1
            time.sleep(0.01)

        if receive_flag == 3:
            if flag_internet_work:
                time.sleep(0.5)
                ic.send_and_wait_answer(robot_address_internet, "start_MTS|" + selected_file_no_dir)
                time.sleep(0.5)
                ic.send_and_wait_answer(robot_address_internet, "startvideo_MTS")
                message_s = ic.send_and_wait_answer(robot_address_internet, "d_MTS")
                message_s = ic.send_and_wait_answer(robot_address_internet, "d_MTS")

            else:
                res = 0
                try:
                    socket.send_string("start|" + selected_file_no_dir)
                    res = socket.recv_string()
                except:
                    pass
                if res == 0:
                    print(FgRed + "Start fail... try again" + Reset)
            receive_flag = 0

        if receive_flag == 4:

            if flag_internet_work:
                print("send file")
                with open(selected_file, 'rb') as myfile:
                    data = myfile.read()
                    # print(ic.send_and_wait_answer(robot_address_internet, "file|" +
                    # selected_file_no_dir + "|" + data.decode("utf-8")))
                #        z = zlib.compress(data, 1).decode("utf-8")
                t1 = time.time()
                ic.clear()
                ic.send_and_wait_answer(robot_address_internet, "file_MTS|" + selected_file_no_dir + "|" + str(
                    base64.b64encode(zlib.compress(data, 1)).decode("utf-8")))

                # read answer from server
                # time.sleep(2)
                # message_s = ic.send_and_wait_answer(robot_address_internet, "d")
                message_s = ""
                while message_s.find(selected_file_no_dir) < 0:
                    message_s = ic.send_and_wait_answer(robot_address_internet, "d_MTS")
                    # print(message_s)
                    # print("Sending file..."+str(round(time.time()-t1,1))+" sec")
                    # printt("Sending file..."+str(round(time.time()-t1,1))+" sec")

                print("Sending file time:" + str(round(time.time() - t1, 3)) + " sec")
                printt("Sending file time:" + str(round(time.time() - t1, 3)) + " sec")

            else:
                res = 0
                try:
                    # print("4 send")
                    socket.send_string("file|" + selected_file_no_dir)
                    res = socket.recv_string()
                    # print("4 send ok", res)
                except:
                    pass
                if res == 0:
                    print(FgRed + "Fail send name file.. try again" + Reset)
                    printt("Fail send name file.. try again", fg='red')
                    return
            receive_flag = 0
            flag_sent_file = True

        if receive_flag == 5:
            if flag_internet_work:
                pass
            else:
                print("open ", selected_file)
                with open(selected_file, 'rb') as myfile:
                    data = myfile.read()
                # print(data)
                # s1 = fastlz.compress(data)
                # s2 = fastlz.decompress(s1)
                # print(len(data), len(s1), len(s2))

                # data = zlib.compress(data, 1)
                data = zlib.compress(data, 1)
                res = 0
                try:
                    socket.send(data)
                    res = socket.recv_string()
                except:
                    pass

                if res == 0:
                    print(FgRed + "Fail send file.. try again" + Reset)
                    printt("Fail send name file.. try again", fg='red')
                    return
                flag_sent_file = True
            receive_flag = 0
        if receive_flag == 6:
            # коннект

            socket.connect("tcp://" + robot_address + ":%s" % port)

            ip_address = sc.gethostbyname(sc.gethostname())

            # s = socket.recv_string(zmq.NOBLOCK)
            print("Taking robot: ", robot_address)

            otvet = ""
            try:
                # print("take|" + ip_address)
                socket.send_string("take|" + ip_address)
                otvet = socket.recv_string()
                print("Connected to robot: " + BgGreen + otvet + Reset)
                printt("Connected to robot: " + otvet, fg='white', bg='green')
            except:
                pass

            pass
            receive_flag = 0
            # printt("Connected to robot: " + otvet, fg='white', bg='green')
        # if receive_flag == 0:
        #     #print("receive flag=0")
        #     time.sleep(0.05)

        time.sleep(0.05)
        # root.after(10, robot_receive_work)
    # except:
    #     #print("except receiver")
    #     pass


#
my_thread_print = threading.Thread(target=robot_receive_work)
my_thread_print.daemon = True
my_thread_print.start()


def Video(ev):
    global receive_flag, root, video_show, robot_address, started_flag, selected_file_no_dir, selected_file, \
        video_show2, video_show2_global
    # video_show2 = 1
    if robot_address == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')

        return
    # if selected_file_no_dir == "":
    #     print("select file!")
    #     return

    # if started_flag == 1:
    #     Stop(ev)

    selected_file_no_dir = "/raw.py"
    # dir = os.path.abspath(os.curdir).replace("starter", '')
    dir = os.path.abspath(os.curdir)
    selected_file = dir.replace("\\", "/") + selected_file_no_dir
    # print(selected_file)

    Start(ev)

    # socket.send_string("start|" + selected_file_no_dir)
    # res = socket.recv_string()

    started_flag = 1

    video_show2_global = 1
    video_show2 = 0
    receive_flag = 1

    print(BgGreen + "RAW ON" + Reset)


def Video2(ev):
    global root, video_show2, robot_address, socket2, video_show2_global, video_show_work
    if robot_address == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')
        return

    if video_show2_global == 0:
        video_show2_global = 1
        video_show2 = 0

        print(FgYellow + "Video ON")
        # root.after(100, ShowVideo2)
    else:
        video_show2_global = 0
        video_show2 = 0
        # print(video_show_work)
        # while video_show_work == True:
        #     print("wait...")
        #     pass

        print(FgYellow + "Video2 OFF")
        # cv2.destroyAllWindows()
        # socket2.close()


def Quit(ev):
    global root
    root.destroy()


def send_selected_file(show_text=False):
    global selected_file, robot_address, selected_file_no_dir, receive_flag, flag_internet_work, flag_sent_file

    flag_sent_file = False
    # print("sending...", video_show2, receive_flag)
    # отсылка через интернет
    if flag_internet_work:
        # print("send_selected_file1")
        time.sleep(0.1)
        receive_flag = 4
        while not flag_sent_file:
            time.sleep(0.01)
        # print("send_selected_file ok")
    else:
        # отсылка по локалке
        time.sleep(0.1)
        receive_flag = 4
        # print("send log: receive flag = ", receive_flag)
        # посылаем заголовок
        while receive_flag == 4:
            # print("send log: receive flag = ", receive_flag)
            time.sleep(0.01)
            pass

        # посылаем сам файл
        # print("send log: receive flag = ", receive_flag)
        receive_flag = 5
        while receive_flag == 5:
            # print("send log: receive flag = ", receive_flag)
            time.sleep(0.01)
            pass

    started_flag = 0
    time.sleep(0.1)
    # cv2.destroyAllWindows()

    if show_text:
        print(FgBlue + "sended ", selected_file_no_dir)
        printt("sended " + selected_file_no_dir, fg='blue')

    pass


def Start(ev):
    global root, robot_address, video_show2, video_show2_global, started_flag, receive_flag, flag_internet_work
    # global socket

    # video_show2 = 1
    if robot_address == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg='red')
        return
    if selected_file_no_dir == "":
        print(FgRed + "select file!" + Reset)
        printt("select file", fg='red')
        return

    Stop(ev)
    print(FgBlue + "Send script")
    printt("Send script", fg='blue')
    # print("send")
    send_selected_file()

    # textbox.delete('1.0', 'end')

    # if flag_internet_work:
    #     time.sleep(0.5)
    #     ic.send_and_wait_answer(robot_address_internet, "start|" + selected_file_no_dir)
    #     time.sleep(0.5)
    #     ic.send_and_wait_answer(robot_address_internet, "startvideo")
    # ic.clear()
    #    else:
    #        res = 0
    #        try:
    # socket.send_string("start|" + selected_file_no_dir)
    # res = socket.recv_string()
    receive_flag = 3
    # print(receive_flag)
    # res=1
    # except:
    #     pass

    while receive_flag == 3:
        pass
    print(FgBlue + "starting..." + FgBlue + selected_file_no_dir)
    printt("starting..." + selected_file_no_dir, fg='blue')
    # time.sleep(2.5)
    started_flag = 1

    if video_show2_global == 1:
        # print("restart video")
        video_show2 = 0
    receive_flag = 1

    # root.after(10, receive_from_robot)


def Stop(ev):
    global root, video_show2, video_show2_global, started_flag, receive_flag, robot_address, socket2

    if robot_address == "-1":
        print(FgRed + "select robot")
        printt("select robot", fg="red")
        return

    if video_show2 != 3:
        video_show2 = -1

    if flag_internet_work:
        # receive_flag == -1
        time.sleep(0.1)
        # ic.send_and_wait_answer(robot_address_internet, "stopvideo")
        # # print("stop")
        # ic.send_and_wait_answer(robot_address_internet, "stop")
        time.sleep(0.1)
        # while 1:
        #     message_s = ic.take_answer()
        #     print(message_s)
        #     if message_s[2]=='':
        #         break

        # ic.clear()

        # return

    # if video_show2_global == 1:
    count = 0
    while video_show2 != 3:
        if count > 20:
            # print(BgRed + "break Video Stop" + Reset)
            break
        count += 1
        # print("wait STOPPED video", video_show2)
        time.sleep(0.05)

    receive_flag = -1
    count = 0
    while receive_flag != 0:
        if count > 100:
            print(BgRed + "break Stop" + Reset)
            break
        count += 1
        time.sleep(0.05)

    # print("STOPPED, ", video_show2, receive_flag)

    # socket.send_string("stop")
    # # socket2.disable_monitor()
    # print(socket.recv_string())
    started_flag = 0
    time.sleep(0.1)
    cv2.destroyAllWindows()


def LoadFile(ev):
    global selected_file, robot_address, selected_file_no_dir

    if robot_address == "-1":
        print(FgRed + "select robot!")
        printt("select robot!", fg='red')
        return
    #
    # my_thread_stop = threading.Thread(target=Stop, args=[(ev,)])
    # my_thread_stop.daemon = True
    # my_thread_stop.start()
    Stop(ev)

    # fn = tkFileDialog.Open(root, filetypes=[('*.py files', '.py')]).show()
    fn = tkFileDialog.askopenfilename(filetypes=[('*.py files', '.py'), ('*.* files', '*.*')])
    if fn == '':
        return
    # print("load2")

    selected_file = fn
    # print(selected_file)
    s = fn.split("/")
    selected_file_no_dir = s[len(s) - 1]
    # print(s[len(s) - 1])

    # print(selected_file)
    root.title(selected_file)

    Start(ev)
    # send_selected_file(True)

    # textbox.delete('1.0', 'end')
    # textbox.insert('1.0', open(fn, 'rt').read())


# def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
#     ## do something
#     global robot_address, socket, receive_flag
#     print(FgBlue,event)
#
#     if event == "none" or robot_address != "-1":
#         print("return")
#         return
#
#     if event[0] == "scan":
#         ScanRobots(event)
#         return
#     robot_address = event[1]
#     # socket = context.socket(zmq.REP)
#     socket = context.socket(zmq.REQ)
#     socket.connect("tcp://" + robot_address + ":%s" % port)
#
#     ip_address = sc.gethostbyname(sc.gethostname())
#
#     # s = socket.recv_string(zmq.NOBLOCK)
#
#     print("Taking robot..", robot_address)
#     socket.send_string("take|" + ip_address)
#     print("Connected to robot: "+BgGreen+socket.recv_string()+Reset)
#     # receive_flag = 1
#
#     connect_keyboard(robot_address)
#     flag_internet_work = False
#     pass


def OptionMenu_SelectionEvent(event):  # I'm not sure on the arguments here, it works though
    # do something
    global robot_address, receive_flag, flag_internet_work, robot_address_internet, started_flag
    # global socket
    print(FgBlue, event)

    # if event == "none" or robot_address != "-1":
    #     print("return")
    #     return

    if event[0] == "scan":
        # ScanRobots(event)
        return

    if event[0] == "scan_internet":
        ip_address_s = sc.gethostbyname(sc.gethostname())
        list_combobox.clear()
        print(ip_address_s)
        print("connect to server...")
        printt("connect to server...")
        time.sleep(0.01)
        ic.connect()
        print("take list")
        printt("take list")
        list = ic.take_list()
        # print(list)
        # print(ic.take_list())
        # list_combobox_internet = []
        # list_combobox_internet.append(["scan_internet", " "])
        time.sleep(0.01)
        for r in list:
            print(r)
            printt(str(r[1]))
            if r[2] == "robot":
                list_combobox.append(r)
        if len(list) == 0:
            print("no robots in server list")
            printt("no robots in server list")

        list_combobox.append(["scan_internet", " "])
        dropVar = tk.StringVar()
        dropVar.set(list_combobox_internet[0])

        combobox_internet = tk.OptionMenu(panelFrame, dropVar, *list_combobox, command=OptionMenu_SelectionEvent)
        combobox_internet.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме
        # print("end take")
        return

    if event[3] == "l":
        robot_address = event[1]
        robot_address_internet = event[0]
        # socket = context.socket(zmq.REP)

        receive_flag = 6
        while receive_flag == 6:
            pass

        # socket = context.socket(zmq.REQ)
        # socket.connect("tcp://" + robot_address + ":%s" % port)
        #
        # ip_address = sc.gethostbyname(sc.gethostname())
        #
        # # s = socket.recv_string(zmq.NOBLOCK)
        #
        # print("Taking robot..", robot_address)
        # try:
        #     socket.send_string("take|" + ip_address)
        #     print("Connected to robot: " + BgGreen + socket.recv_string() + Reset)
        # except:
        #     pass

        # receive_flag = 1
        flag_internet_work = False

    if event[3] == "i":

        robot_address_internet = event[0]
        robot_address = event[0]
        print(robot_address_internet)
        printt(robot_address_internet)
        flag_internet_work = True
        ic.clear()
        for i in range(5):
            message_s = ic.send_and_wait_answer(robot_address_internet, "d_MTS")
        print("Connected to robot: " + BgGreen + event[1] + Reset)
        printt("Connected to robot: " + event[1], bg='green', fg='white')
        ic.clear()

        receive_flag = 1
        started_flag = 1
        pass
    connect_keyboard(robot_address)
    pass


#
# def test(ev):
#     # print(ic.send_and_wait_answer(robot_address_internet,"d"))
#     # ic.send_and_wait_answer(robot_address_internet, "stopvideo|")
#
#
#     m = ic.send_and_wait_answer(robot_address_internet, "p")
#     print(m)
#     time.sleep(0.5)
#     j_mesg, jpg_bytes = ic.take_answer_bytes()
#     if j_mesg == "-1":
#         print("error json")
#         return
#     print(j_mesg, len(jpg_bytes))
#     md = json.loads(j_mesg)
#     A = np.frombuffer(jpg_bytes, dtype=md['dtype'])
#     # arrayname = md['arrayname']sccv2.waitKey(1)
#
#     image = A.reshape(md['shape'])
#     image = cv2.imdecode(image, 1)
#     cv2.imshow("Robot frame", image)
#     cv2.waitKey(1)
#     time.sleep(1)

#
# def ScanRobots(ev):
#     global panelFrame, socket, robot_address, video_show
#
#     ip_address_s = sc.gethostbyname(sc.gethostname())
#     print(ip_address_s)
#     ip_address = ip_address_s.split(".")
#     ip_address[0] = "192"
#     ip_address[1] = "168"
#     ip_address[2] = "88"
#     if robot_address != "-1":
#         Stop(ev)
#         print("drop robot")
#         socket = context.socket(zmq.REQ)
#         print(robot_address)
#         socket.connect("tcp://" + robot_address + ":%s" % port)
#         print("send", "tcp://" + robot_address + ":%s" % port)
#         try:
#             socket.send_string("drop")
#             print(socket.recv_string())
#         except:
#             pass
#
#         robot_address = "0"
#         video_show = 0
#
#     list_combobox = ["none"]
#     dropVar = StringVar()
#     dropVar.set(list_combobox[0])
#
#     for i in range(20, 30):
#
#         socket = context.socket(zmq.REQ)
#         ip_address_ping = str(ip_address[0] + "." + ip_address[1] + "." + ip_address[2] + "." + str(i))
#         # socket.connect("tcp://"+ip_address[0]+"."+ip_address[1]+"."+ip_address[2]+"."+str(i)+":%s" % port)
#         socket.connect("tcp://" + ip_address_ping + ":%s" % port)
#         print("ping", ip_address_ping)
#         # print("send")
#         try:
#             socket.send_string("ping")
#         except:
#             pass
#         time.sleep(0.7)
#
#         s = ""
#         try:
#             # print("recv...")
#             s = socket.recv_string(zmq.NOBLOCK)
#             # print("....ok")
#         except zmq.ZMQError as e:
#             if e.errno == zmq.ETERM:
#                 return  # shutting down, quit
#                 print("no server")
#
#         data = s.split("|")
#         if len(data) > 1:
#             s = data[0] + " " + data[1] + " " + str(ip_address_ping) + "\n"
#             if len(s) > 2:
#                 print(FgMagenta + s + Reset)
#
#             if data[1] == ip_address_s:
#                 dropVar.set(ip_address_ping)
#                 robot_address = ip_address_ping
#                 socket = context.socket(zmq.REQ)
#                 socket.connect("tcp://" + robot_address + ":%s" % port)
#                 # data[1] = "Connected"
#                 list_combobox.append(data[1])
#                 connect_keyboard(robot_address)
#                 print(FgBlue + "Connected to robot: " + BgGreen + data[0] + Reset)
#                 # дальше не ищем
#                 break
#
#             if data[1] == "0":
#                 data[1] = ip_address_ping
#                 list_combobox.append(data)
#
#     # combobox = OptionMenu(panelFrame, dropVar, *list)
#     # combobox.place(x=250, y=10, width=250, height=40)  # Позиционируем Combobox на форме
#
#     # var = StringVar()
#     # combobox = OptionMenu(panelFrame, dropVar, *(list), command=OptionMenu_SelectionEvent)
#     combobox = OptionMenu(panelFrame, dropVar, *(list_combobox), command=OptionMenu_SelectionEvent)
#     combobox.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме
#
#     # fn = tkFileDialog.SaveAs(root, filetypes=[('*.py files', '.py')]).show()
#     # if fn == '':
#     #     return
#     # if not fn.endswith(".txt"):
#     #     fn += ".txt"
#     # open(fn, 'wt').write(textbox.get('1.0', 'end'))
#     pass
#

def mouse_move():
    global mouse_x, mouse_y
    x1 = 0
    y1 = 0
    while 1:
        x, y = mouse.get_position()

        if x1 != x or y1 != y:
            # send_event(data)
            x1 = x
            y1 = y
            mouse_x = x
            mouse_y = y
            # print("mouse", x,y)
        time.sleep(0.001)


if MOUSE_FLAG:
    my_thread_mouse = threading.Thread(target=mouse_move)
    my_thread_mouse.daemon = True
    my_thread_mouse.start()


def joy_move():
    global joy_x, joy_y
    x = 1
    y = 1

    while 1:
        pygame.event.get()
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        if joystick_count > 0:

            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # 0 газ
            joy_x1 = joystick.get_axis(2)
            joy_y1 = joystick.get_axis(1)
            # print(joystick.get_numaxes())
            # print(joystick.get_axis(1))

            if x != joy_x1 or y != joy_y1:
                # send_event(data)
                x = joy_x1
                y = joy_y1
                joy_x = np.interp(joy_x1, [-1, 1], [-255, 255])
                joy_y = np.interp(joy_y1, [-1, 1], [-255, 255])
                # print((joy_x, joy_y))
                continue

        time.sleep(0.001)
        # return joystick.get_axis(0), joystick.get_axis(1)


if JOYSTICK_FLAG:
    my_thread_joy = threading.Thread(target=joy_move)
    my_thread_joy.daemon = True
    my_thread_joy.start()


def make_dataset():
    global FRAME, key_pressed_dataset
    count = 2000
    X = np.ndarray(shape=(count, 120, 160, 3), dtype=np.uint8)
    Y = np.ndarray(shape=(count, 1), dtype=np.float32)
    Z = np.ndarray(shape=(count, 1), dtype=np.float32)
    count_frames = 0
    while 1:
        # if type(FRAME)=="<class 'int'>":
        if type(FRAME) is int:
            # print (str(type(FRAME)))
            pass
        else:

            j_x = joy_x
            j_y = joy_y

            if key_pressed_dataset != 0:
                print(key_pressed_dataset)

                cv2.imshow("dataset_key", FRAME)
                cv2.waitKey(1)

                # frame = cv2.cvtColor(FRAME, cv2.COLOR_BGR2RGB)
                frame = FRAME.copy()
                X[count_frames] = cv2.resize(frame, (160, 120), interpolation=cv2.INTER_CUBIC)
                t = 0.5
                if key_pressed_dataset == 39:
                    t = 0
                if key_pressed_dataset == 37:
                    t = 1

                Y[count_frames] = t
                Z[count_frames] = key_pressed_dataset

                print(j_x, j_y)

                count_frames += 1
                print(count_frames)

                if count_frames >= count:
                    with open("train.pkl", "wb") as f:
                        pickle.dump([X, Y, Z], f)
                    print("save dataset")
                    return
                key_pressed_dataset = 0

            if abs(j_x) > 1 and abs(j_y) > 1:

                cv2.imshow("dataset", FRAME)
                cv2.waitKey(1)

                frame = cv2.cvtColor(FRAME, cv2.COLOR_BGR2RGB)
                X[count_frames] = cv2.resize(frame, (160, 120), interpolation=cv2.INTER_CUBIC)
                Y[count_frames] = j_y
                Z[count_frames] = j_x

                print(j_x, j_y)

                count_frames += 1
                print(count_frames)

                if count_frames >= count:
                    with open("train.pkl", "wb") as f:
                        pickle.dump([X, Y, Z], f)
                    print("save dataset")
                    return

        time.sleep(0.1)
        # return joystick.get_axis(0), joystick.get_axis(1)


#
if DATASET:
    my_thread_dataset = threading.Thread(target=make_dataset)
    my_thread_dataset.daemon = True
    my_thread_dataset.start()


def send_event():
    global socket3, started_flag, ic_key, receive_flag, key_started, key_pressed, mouse_x, mouse_y, joy_x, joy_y
    context3 = zmq.Context()
    socket3 = context3.socket(zmq.REQ)
    ic_key = InetConnection.InetConnect(sc.gethostname() + "_key", "client")
    while 1:
        if key_started == -1:
            time.sleep(0.1)
            continue

        if key_started == 0:
            if flag_internet_work:
                ic_key.connect()
                # print("start key client")
            else:
                socket3.connect("tcp://" + robot_address + ":5559")
            key_started = 1
            break

    j_x = -1
    j_y = -1
    while 1:

        data = ""
        if key_pressed != 0:
            data = key_pressed
            key_pressed = 0
        else:
            if mouse_x != -1 and mouse_y != -1:
                data = "m," + str(mouse_x) + "," + str(mouse_y)
                mouse_x = -1
                mouse_y = -1
            if joy_x != j_x or joy_y != j_y:
                data = "j," + str(round(joy_x, 2)) + "," + str(round(joy_y, 2))
                # print(joy_x, joy_y)
                j_x = joy_x
                j_y = joy_y

        # if data!="":
        #     print(data, receive_flag)

        # if data != "" and receive_flag == 1:
        if data != "":
            # print("DATA", data)
            if flag_internet_work:
                ic_key.send_key(robot_address_internet, str(data))

            else:
                if receive_flag == 1:
                    # socket3.send_string(str(data))
                    # print("send",data)
                    try:
                        socket3.send_string(str(data), zmq.NOBLOCK)  # zmq.NOBLOCK
                    except:
                        pass

                    message = ""
                    count = 0
                    while 1:
                        count += 1
                        try:
                            # print("s1")
                            # socket2.send_string("p", zmq.NOBLOCK)
                            message = socket3.recv_string(zmq.NOBLOCK)
                            # print("....ok")
                        except zmq.ZMQError as e:
                            pass
                        # print(message)
                        if message == "1":
                            break
                        time.sleep(0.01)
                        if count > 100:
                            # print(BgRed + "reconnect key" + Reset)
                            print("reconnect key" + Reset)
                            socket3.close()
                            # context3 = zmq.Context()
                            socket3 = context3.socket(zmq.REQ)
                            socket3.connect("tcp://" + robot_address + ":5559")
                            break

        time.sleep(0.001)


my_thread_key = threading.Thread(target=send_event)
my_thread_key.daemon = True
my_thread_key.start()


def connect_keyboard(robot_address):
    global flag_internet_work, key_started
    key_started = 0
    pass


def keydown(e):
    global started_flag, receive_flag, key_pressed, fps_show, key_pressed_dataset, FRAME
    key_pressed = e.keycode
    key_pressed_dataset = e.keycode
    if key_pressed == 113:
        print("F2 make screen")
        cv2.imwrite("screen.jpg", FRAME)

    if key_pressed == 112:
        if fps_show == 1:
            fps_show = 0
        else:
            fps_show = 1
    # print(key_pressed)


root = tk.Tk()
root.title('RoboStarter')
root.geometry('420x300+900+10')  # ширина=500, высота=400, x=300, y=200
root.resizable(True, True)  # размер окна может быть изменён только по горизонтали

root.bind("<KeyPress>", keydown)

panelFrame = tk.Frame(root, height=55, bg='gray')
textFrame = tk.Frame(root, height=200, width=500)

panelFrame.pack(side='top', fill='x')
textFrame.pack(side='bottom', fill='both', expand=1)

# tex.pack(side=tk.RIGHT)
textbox = tk.Text(textFrame, font='Arial 10', wrap='word')

scrollbar = tk.Scrollbar(textFrame)

scrollbar['command'] = textbox.yview
textbox['yscrollcommand'] = scrollbar.set

textbox.pack(side='left', fill='both', expand=1)
scrollbar.pack(side='right', fill='y')

loadBtn = tk.Button(panelFrame, text='Load\nStart')
# saveBtn = Button(panelFrame, text='Scan')
startBtn = tk.Button(panelFrame, text='Start')
stopBtn = tk.Button(panelFrame, text='Stop')
videoBtn = tk.Button(panelFrame, text='Raw')
videoBtn2 = tk.Button(panelFrame, text='Video')
# testBtn = Button(panelFrame, text='test')

loadBtn.bind("<Button-1>", LoadFile)
# saveBtn.bind("<Button-1>", ScanRobots)
startBtn.bind("<Button-1>", Start)
stopBtn.bind("<Button-1>", Stop)
videoBtn.bind("<Button-1>", Video)
videoBtn2.bind("<Button-1>", Video2)
# testBtn.bind("<Button-1>", test)

loadBtn.place(x=10, y=10, width=40, height=40)
# saveBtn.place(x=10, y=10, width=40, height=40)
startBtn.place(x=60, y=10, width=40, height=40)
stopBtn.place(x=110, y=10, width=40, height=40)
videoBtn.place(x=160, y=10, width=40, height=40)
videoBtn2.place(x=210, y=10, width=40, height=40)

# testBtn.place(x=10, y=60, width=40, height=40)
# root.after(10, robot_receive_work)
#
list_combobox = []

list_combobox_internet = []
dropVar = tk.StringVar()
dropVar.set("Connect to robot")
dropVar_internet = tk.StringVar()
dropVar_internet.set("Connect to robot")
# list_combobox.append(["0", "192.168.88.20", "robot", "l"])
# list_combobox.append(["1", "192.168.88.21", "robot", "l"])
# list_combobox.append(["2", "192.168.88.22", "robot", "l"])
# list_combobox.append(["3", "192.168.88.23", "robot", "l"])
# list_combobox.append(["4", "192.168.88.24", "robot", "l"])
# list_combobox.append(["5", "192.168.88.25", "robot", "l"])
# list_combobox.append(["6", "192.168.88.26", "robot", "l"])
# list_combobox.append(["7", "192.168.88.27", "robot", "l"])
# list_combobox.append(["8", "192.168.88.28", "robot", "l"])
# list_combobox.append(["9", "192.168.88.29", "robot", "l"])

# list_combobox.append(["0_eth","192.168.88.30", "robot", "l"])
# list_combobox.append(["1_eth","192.168.88.31", "robot", "l"])
# list_combobox.append(["2_eth","192.168.88.32", "robot", "l"])
# list_combobox.append(["3_eth", "192.168.88.33", "robot", "l"])
# list_combobox.append(["4_eth","192.168.88.34", "robot", "l"])
# list_combobox.append(["5_eth","192.168.88.35", "robot", "l"])
# list_combobox.append(["6_eth","192.168.88.36", "robot", "l"])
# list_combobox.append(["scan", " "])
list_combobox.append(["scan_internet", " "])
list_combobox_internet.append(["scan_internet", " "])

combobox = tk.OptionMenu(panelFrame, dropVar, *list_combobox, command=OptionMenu_SelectionEvent)
combobox.place(x=260, y=10, width=150, height=40)  # Позиционируем Combobox на форме


# combobox_internet = OptionMenu(panelFrame, dropVar_internet, *(list_combobox_internet),
# command=OptionMenu_SelectionEvent_internet)
# combobox_internet.place(x=260, y=60, width=150, height=40)  # Позиционируем Combobox на форме

def ppp(text, fg='black', bg='white'):
    global textbox, started_flag, root

    # data = textbox.get('1.0', END + '-1c')
    # print("printt", text)
    textbox.configure(state='normal')
    data = textbox.get('1.0', 'end-1c')

    data = data.split('\n')

    text_list = text.split("\n")

    # print()
    count = len(data)

    if count > 1000:
        textbox.delete('1.0', '500.0')
        data = textbox.get('1.0', 'end-1c')

        data = data.split('\n')

        text_list = text.split("\n")

    # print()
    count = len(data)

    textbox.insert('end', str(text) + "\n")
    textbox.see('end')  # Scroll if necessary
    # print(str(count) + ".0", str(count) + ".20")
    textbox.tag_add(str(count), str(count) + ".0", str(count) + str(len(text_list)) + ".200")
    # textbox.tag_add("start", "1.8", "1.13")
    # textbox.tag_config("here", background="yellow", foreground="blue")
    textbox.tag_config(str(count), foreground=fg, background=bg)
    #
    if started_flag:
        textbox.configure(state='disabled')


def printt(text, fg='black', bg='white'):
    my_thread = threading.Thread(target=ppp, args=(text, fg, bg,))
    my_thread.daemon = True
    my_thread.start()


# def kill_cv():
#     global started_flag
#     if started_flag==False:
#         cv2.destroyAllWindows()
#     time.sleep(1)
#
#
# my_thread = threading.Thread(target=kill_cv)
# my_thread.daemon = True
# my_thread.start()

print("Start robot API")

printt("Start robot API", fg='green')

root.mainloop()

#
# import tkinter as tk
#
# def cbc(id, tex):
#     return lambda : callback(id, tex)
#
# def callback(id, tex):
#     s = 'At {} f is {}\n'.format(id, id**id/0.987)
#     tex.insert(tk.END, s)
#     tex.see(tk.END)             # Scroll if necessary
#
# top = tk.Tk()
# tex = tk.Text(master=top)
# tex.pack(side=tk.RIGHT)
# bop = tk.Frame()
# bop.pack(side=tk.LEFT)
# for k in range(1,10):
#     tv = 'Say {}'.format(k)
#     b = tk.Button(bop, text=tv, command=cbc(k, tex))
#     b.pack()
#
# tk.Button(bop, text='Exit', command=top.destroy).pack()
# top.mainloop()
