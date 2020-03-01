import cv2
import numpy
from matplotlib import pyplot as plt

# cv2.namedWindow("frame")
# cv2.namedWindow("disparity")
# cv2.namedWindow("images")
# cv2.namedWindow("imgL")
capture = cv2.VideoCapture()
capture.open(0)

window_size = 5
min_disp = 32
num_disp = 112 - min_disp
stereo = cv2.StereoSGBM_create(minDisparity=-2, numDisparities=16, blockSize=18)
scale = 2
i = 0
while i == 0:
    s, frame = capture.read()
    # frame = cv2.blur(frame, (10, 10))
    cv2.imshow("frame", frame)
    frame = cv2.resize(frame, (0, 0), fx=1/scale, fy=1/scale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgL = gray[0:int(240/scale), 0:int(320/scale)].copy()
    imgR = gray[0:int(240/scale), int(320/scale):int(640/scale)].copy()
    disparity = stereo.compute(imgL, imgR)
    qw = cv2.normalize(disparity, disparity, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    cv2.imshow("disparity", qw)
    # cv2.imshow("imgL", imgL)
    # cv2.imshow("imgR", imgR)

    k = cv2.waitKey(10)
    if k == ord('s') or k == ord('ы'):
        cv2.destroyAllWindows()
        capture.release()
        break
