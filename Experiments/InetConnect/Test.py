import PromobotAPI as PromobotAPI
import cv2
import keyboard
import time

robot = PromobotAPI.PromobotAPI(flag_serial=False)
while True:
    robot.set_frame(robot.get_frame())
    if robot.manual(1) == 1:
        continue
