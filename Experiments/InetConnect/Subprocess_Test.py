import subprocess
import time

# args = ["C://Anaconda3//python.exe", "C://Robot//Simple.py"]
args = ['C:/Users/terle/Desktop/script.bat']
# process = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

# proc = True
# proc = await asyncio.create_subprocess_exec(
#     'python3', 'print1.py', stdout=slave, stderr=slave)
#    'python3', dir + filename, stdout=slave, stderr=slave)
# 'python3', 'robot_keras2.py', stdout = slave, stderr = slave)
# 'python3', 'manual_client.py', stdout = slave, stderr = slave)
# 'python3', 'robot_keras.py', stdout=slave, stderr=slave)
# 'python3', 'print1.py', stdout=asyncio.subprocess.PIPE)

# stdout, stderr = await proc.communicate()
while process.poll() is None:
    try:
        # console_out += str(os.read(master, 4096).decode("utf-8"))
        print(process.stdout.readline().strip())
    except:
        print("Error")
        pass
    time.sleep(0.01)
