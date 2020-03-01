import cv2

cap1 = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)

while True:
    _, frame1 = cap1.read()
    _, frame2 = cap2.read()
    cv2.imshow("frame1", frame1)
    cv2.imshow("frame2", frame2)
    cv2.waitKey(1)
