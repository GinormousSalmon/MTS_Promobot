import MTS.PromobotAPI as PromobotAPI
import time

robot = PromobotAPI.PromobotAPI(flag_serial=False, flag_lidar=False, flag_tts=True, voice_type=1)
robot.say("Hello")
robot.say("Hello")

time.sleep(1)
