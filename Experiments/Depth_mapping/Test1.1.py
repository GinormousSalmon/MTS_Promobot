import cv2
import numpy
from matplotlib import pyplot as plt

# cv2.namedWindow("frame")
# cv2.namedWindow("disparity")
# cv2.namedWindow("images")
# cv2.namedWindow("imgL")
capture = cv2.VideoCapture()
capture.open(0)

stereo = cv2.StereoSGBM_create(minDisparity=-2, numDisparities=16, blockSize=18)
low = numpy.array((0, 0, 255))
high = numpy.array((255, 255, 255))

scale = 2
i = 0
while i == 0:
    s, frame = capture.read()
    # frame = cv2.blur(frame, (10, 10))
    cv2.imshow("frame", frame)
    frame = cv2.resize(frame, (0, 0), fx=1 / scale, fy=1 / scale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgL = gray[0:int(240 / scale), 0:int(320 / scale)].copy()
    imgR = gray[0:int(240 / scale), int(320 / scale):int(640 / scale)].copy()
    disparity = stereo.compute(imgL, imgR)
    qw = cv2.normalize(disparity, disparity, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    bgr = cv2.cvtColor(qw, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    found = False
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), 1)
            found = True
    cv2.imshow("disparity", mask)
    # cv2.imshow("imgL", imgL)
    # cv2.imshow("imgR", imgR)

    k = cv2.waitKey(1)
    if k == ord('s') or k == ord('ы'):
        cv2.destroyAllWindows()
        capture.release()
        break
