import subprocess
import threading
import cv2
import numpy

frame = numpy.zeros((512, 512, 3), numpy.uint8)
frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
width = frame.shape[1]
height = frame.shape[0]
angle = 0.00
angle_old = 0.00
distance = 0.00
dots = []
index = 0


def frame_work():
    global width, height, frame, dots
    while True:
        cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 0), max(width, height))
        for ang, dist in dots:
            try:
                ang = ang * numpy.pi / 180
                x1 = dist * numpy.sin(ang)
                y1 = dist * numpy.cos(ang)
                x1 = int(width / 2 + x1 * 0.05)
                y1 = int(height / 2 - y1 * 0.05)
                cv2.rectangle(frame, (x1, y1), (x1, y1), (255, 255, 255), 2)
            except:
                pass
        canny = cv2.Canny(frame, cv2.getTrackbarPos("param1", "frame"), cv2.getTrackbarPos("param2", "frame"),
                          apertureSize=3)
        im2, contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_frame = frame.copy()
        contour_frame = cv2.cvtColor(contour_frame, cv2.COLOR_GRAY2BGR)
        x1 = int(width / 2)
        y1 = int(height / 2)
        cv2.drawContours(contour_frame, contours, -1, (200, 0, 0), 1)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w * h > 10:
                cv2.rectangle(contour_frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
        frame_show = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(contour_frame, (x1, y1), (x1, y1), (0, 255, 0), 3)
        cv2.rectangle(frame_show, (x1, y1), (x1, y1), (0, 255, 0), 3)
        cv2.imshow("frame", numpy.hstack([frame_show, contour_frame]))
        cv2.waitKey(1)


def nothing(x):
    pass


cv2.createTrackbar('param1', 'frame', 10, 300, nothing)
cv2.createTrackbar('param2', 'frame', 10, 300, nothing)

process = subprocess.Popen("C:/Users/terle/Desktop/МТС/Lidar/rplidar_sdk_v1.7.0/tools/win32/ultra_simple.exe //./com10",
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)  # указать путь к ultra_simple.exe и com порт

thread = threading.Thread(target=frame_work)
thread.daemon = True
thread.start()

while process.poll() is None:
    try:
        data = str(process.stdout.readline().decode("utf-8").strip())
    except:
        continue
    # print(data)
    angle_old = angle
    try:
        angle = float(data[7:(data.find(".") + 3)])
        distance = float(data[(data.rfind(".") - 5):(data.rfind(".") + 3)])
    except:
        continue
    if angle < angle_old:
        if len(dots) > index:
            for i in range(index, len(dots)):
                dots.pop()
        index = 0
    if index + 1 > len(dots):
        dots.append((angle, distance))
    else:
        dots[index] = (angle, distance)
    index += 1
