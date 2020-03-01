import cv2
import numpy as np

capture = cv2.VideoCapture()
capture.open(0)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

object_point = np.zeros((6 * 8, 3), np.float32)
object_point[:, :2] = np.mgrid[0:8, 0:6].T.reshape(-1, 2)

object_points = []
object_points2 = []
image_points_left = []
image_points_right = []
scale = 0.4


def nothing(x):
    pass


stereo = cv2.StereoSGBM_create(
    minDisparity=-16,
    numDisparities=96,
    uniquenessRatio=1,
    speckleWindowSize=150,
    speckleRange=2,
    disp12MaxDiff=10,
    P1=600,
    P2=2400
    , blockSize=5, preFilterCap=4)

cv2.namedWindow("Trackbars", flags=cv2.WINDOW_FREERATIO)
cv2.namedWindow("frame", flags=cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('minDisparity', 'Trackbars', 134, 300, nothing)
cv2.createTrackbar('numDisparities', 'Trackbars', 6, 15, nothing)
cv2.createTrackbar('uniquenessRatio', 'Trackbars', 1, 10, nothing)
cv2.createTrackbar('speckleWindowSize', 'Trackbars', 150, 400, nothing)
cv2.createTrackbar('speckleRange', 'Trackbars', 2, 10, nothing)
cv2.createTrackbar('disp12MaxDiff', 'Trackbars', 10, 100, nothing)
cv2.createTrackbar('P1', 'Trackbars', 600, 1000, nothing)
cv2.createTrackbar('P2', 'Trackbars', 2400, 10000, nothing)
cv2.createTrackbar('blockSize', 'Trackbars', 5, 30, nothing)
cv2.createTrackbar('preFilterCap', 'Trackbars', 4, 30, nothing)

while 1:
    _, frame = capture.read()
    cv2.imshow("cam", frame)
    frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgL = frame[0:int(240 * scale), 0:int(320 * scale)].copy()
    imgR = frame[0:int(240 * scale), int(320 * scale):int(640 * scale)].copy()

    stereo = cv2.StereoSGBM_create(
        minDisparity=int(cv2.getTrackbarPos("minDisparity", "Trackbars") - 150),
        numDisparities=int((cv2.getTrackbarPos("numDisparities", "Trackbars")+1) * 16),
        blockSize=int(cv2.getTrackbarPos("blockSize", "Trackbars")))
    # stereo = cv2.StereoBM_create(numDisparities=32, blockSize=15)
    print(int(cv2.getTrackbarPos("minDisparity", "Trackbars") - 150),
          int((cv2.getTrackbarPos("numDisparities", "Trackbars")+1) * 16),
          int(cv2.getTrackbarPos("uniquenessRatio", "Trackbars")),
          int(cv2.getTrackbarPos("speckleWindowSize", "Trackbars")),
          int(cv2.getTrackbarPos("speckleRange", "Trackbars")),
          int(cv2.getTrackbarPos("disp12MaxDiff", "Trackbars")), int(cv2.getTrackbarPos("P1", "Trackbars")),
          int(cv2.getTrackbarPos("P2", "frame")), int(cv2.getTrackbarPos("blockSize", "Trackbars")),
          int(cv2.getTrackbarPos("preFilterCap", "Trackbars")))

    disparity = stereo.compute(imgL, imgR)
    qw = cv2.normalize(disparity, disparity, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    cv2.imshow('frame', qw)
    # print(disparity[320][240])

    k = cv2.waitKey(1)
    if k == 27:
        cv2.destroyAllWindows()
        break
