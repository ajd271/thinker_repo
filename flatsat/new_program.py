"""
All functions here are complete, please you this to test your 
sensor_calc.py functions.
"""

#import libraries
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
import time
import os
import board
import busio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import sys
from git import Repo
sys.path.append('/path/to/directory/containing/sensor_calc_V2')
from sensor_calc_V2 import *
from picamera2 import Picamera2
from multiprocessing import Process
#imu initialization
i2c = busio.I2C(board.SCL, board.SDA)
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
xs = []
y1 = []
y2 = []
y3 = []
rpy = [0,0,0]
THRESHOLD = 0.02      #Any desired value from the accelerometer
REPO_PATH = "/home/pi/thinker_repo"     #Your github repo path: ex. /home/pi/FlatSatChallenge
FOLDER_PATH = "/flatsat"   #Your image folder path in your GitHub repo: ex. /Images
rocket = 0
def animate(i, xs, type,y1,y2,y3, mag_offset, gyro_offset, initial_angle):
    if len(y1) ==0:
        prev_ang = initial_angle
    else:
        a = y1[-1]
        b = y2[-1]
        c = y3[-1]
        prev_ang = [a,b,c]
    accelX, accelY, accelZ = accel_gyro.acceleration #m/s^2
    magX, magY, magZ = mag.magnetic #gauss
    #Calibrate magnetometer readings
    magX = magX - mag_offset[0]
    magY = magY - mag_offset[1]
    magZ = magZ - mag_offset[2]
    gyroX, gyroY, gyroZ = accel_gyro.gyro #rad/s
    gyroX = gyroX * (180/np.pi)- gyro_offset[0]
    gyroY = gyroY * (180/np.pi)- gyro_offset[1]
    gyroZ = gyroZ * (180/np.pi)- gyro_offset[2]
    xs.append(time.time())

    if type == 'am':
       y1.append(roll_am(accelX,accelY,accelZ))
       y2.append(pitch_am(accelX,accelY,accelZ))
       y3.append(yaw_am(accelX,accelY,accelZ,magX,magY,magZ))
       ax.clear()
       ax.plot(xs,y1,label = "Roll")
       ax.plot(xs,y2,label = "Pitch")
       ax.plot(xs,y3,label = "Yaw")
       plt.title('Roll Pitch Yaw, Using Accelerometer and Magnetometer')
       plt.ylabel('deg')

    elif type =='gyro':
       if len(xs) == 1:
           y1.append(prev_ang[0])
           y2.append(prev_ang[1])
           y3.append(prev_ang[2])
       else:
           delT = xs[-1] - xs[-2]
           y1.append(roll_gy(prev_ang[0],delT,gyroY))
           y2.append(pitch_gy(prev_ang[1],delT,gyroX))
           y3.append(yaw_gy(prev_ang[2],delT,gyroZ))

       ax.clear()
       ax.plot(xs,y1,label = "Roll")
       ax.plot(xs,y2,label = "Pitch")
       ax.plot(xs,y3,label = "Yaw")
       plt.title('Roll Pitch Yaw, Using Gyro')
       plt.ylabel('deg')

    else:
       print("Not a valid argument.")
       return
    #Keep the plot from being too long
    xs = xs[-20:]
    y1 = y1[-20:]
    y2 = y2[-20:]
    y3 = y3[-20:]
    plt.grid()
    plt.legend()
    plt.xlabel('Time')

def plot_data(type = 'am'):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"photo_{timestamp}.jpg"
    
    mag_offset = calibrate_mag()
    initial_angle = set_initial(mag_offset)
    gyro_offset = calibrate_gyro()
    ani = animation.FuncAnimation(fig, animate, fargs =(xs,type,y1,y2,y3,mag_offset,gyro_offset,initial_angle), interval = 1000)

    plt.show()
    


def take_photo():
    print("Photo process started")
    while not stop_event.is_set():
        accelx, accely, accelz = accel_gyro.acceleration
        
        if accelx>THRESHOLD and accely>THRESHOLD:
        #CHECKS IF READINGS ARE ABOVE THRESHOLD
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            time.sleep(2) #PAUSE
            name = "ThinkerS"     #First Name, Last Initial  ex. MasonM
            picam2.start_and_capture_file(filename)
           # git_push()
            print("Photo saved successfully") 
            

            


if __name__ == '__main__':
    process1 = Process(target=plot_data, args=('am',))  # Start plot process
    process2 = Process(target=take_photo)  # Start photo-taking process

    process1.start()
    process2.start()

    process1.join()
    process2.join()  # Wait for both processes to finish
    
 



