import MTSAPI as robot
import serial
import time

port = serial.Serial('COM11', 300, timeout=2)
message = "12345678"
time.sleep(1)
port.write(bytes(message.encode('utf-8')))
port.write(bytes("\n".encode('utf-8')))

flag_wait = True
# time.sleep(0.01)
answer = ""
t = time.time()
if flag_wait:
    while not port.in_waiting:
        pass
t = time.time() - t
print(t)
while port.in_waiting:
    answer = answer + str(port.readline())
    answer = answer[2:len(answer) - 5]
print(answer)
