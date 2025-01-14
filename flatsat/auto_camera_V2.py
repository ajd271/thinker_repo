"""
The code below is a template for the auto_camera.py file. You will need to
finish the capture() function to take a picture at a given RPY angle. Make
sure you have completed the sensor_calc.py file before you begin this one.
"""

#import libraries
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
import time
import os
import board
import busio
from picamera2 import Picamera2
import numpy as np
import sys
sys.path.append('/path/to/directory/containing/sensor_calc_V2')
from sensor_calc_V2 import *

#imu and camera initialization
i2c = busio.I2C(board.SCL, board.SDA)
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()


"""
#Code to take a picture at a given offset angle
def capture(dir ='roll', target_angle = 30):
    #Calibration lines should remain commented out until you implement calibration
    offset_mag = calibrate_mag()
    offset_gyro =calibrate_gyro()
    initial_angle = set_initial(offset_mag)
    prev_angle = initial_angle
    print("Begin moving camera.")
    while True:
        accelX, accelY, accelZ = accel_gyro.acceleration #m/s^2
        magX, magY, magZ = mag.magnetic #gauss
	    #Calibrate magnetometer readings
        magX = magX - offset_mag[0]
        magY = magY - offset_mag[1]
        magZ = magZ - offset_mag[2]
        gyroX, gyroY, gyroZ = accel_gyro.gyro #rad/s
        #Convert to degrees and calibrate
        gyroX = gyroX *180/np.pi - offset_gyro[0]
        gyroY = gyroY *180/np.pi - offset_gyro[1]
        gyroZ = gyroZ *180/np.pi - offset_gyro[2]
        
        #TODO: Everything else! Be sure to not take a picture on exactly a
        #certain angle: give yourself some margin for error. 
"""
# Code to take a picture at a given offset angle
def capture(dir='roll', target_angle=30):
    """
    Captures a picture when the target angle offset is achieved.
   
    Parameters:
        dir (str): Direction to monitor ('roll', 'pitch', or 'yaw').
        target_angle (float): Target angle offset to capture the picture.
    """
    # Calibration
    offset_mag = calibrate_mag()
    offset_gyro = calibrate_gyro()
    initial_angle = set_initial(offset_mag)
    prev_angle = initial_angle  # Store the initial RPY angles
    print("Begin moving camera.")

    # Allowable margin for error in angle
    angle_margin = 2  # degrees

    while True:
        # Read accelerometer and magnetometer data
        accelX, accelY, accelZ = accel_gyro.acceleration  # m/s^2
        magX, magY, magZ = mag.magnetic  # gauss
        magX -= offset_mag[0]
        magY -= offset_mag[1]
        magZ -= offset_mag[2]

        # Read gyroscope data
        gyroX, gyroY, gyroZ = accel_gyro.gyro  # rad/s
        gyroX = gyroX * 180 / np.pi - offset_gyro[0]
        gyroY = gyroY * 180 / np.pi - offset_gyro[1]
        gyroZ = gyroZ * 180 / np.pi - offset_gyro[2]

        # Calculate current roll, pitch, and yaw
        roll = roll_am(accelX, accelY, accelZ)
        pitch = pitch_am(accelX, accelY, accelZ)
        yaw = yaw_am(accelX, accelY, accelZ, magX, magY, magZ)

        # Integrate gyroscope data for updated angles
        delT = 0.1  # Time step in seconds (adjust as needed)
        roll = roll_gy(prev_angle[0], delT, gyroX)
        pitch = pitch_gy(prev_angle[1], delT, gyroY)
        yaw = yaw_gy(prev_angle[2], delT, gyroZ)

        # Update previous angles
        prev_angle = [roll, pitch, yaw]

        # Check if the desired angle is achieved within margin
        current_angle = {'roll': roll, 'pitch': pitch, 'yaw': yaw}[dir]
        if abs(current_angle - target_angle) <= angle_margin:
            print(f"Target angle reached: {dir} = {current_angle:.2f}°")
            picam2.capture_file(f"{dir}_{int(time.time())}.jpg")
            print(f"Picture taken at {dir} = {current_angle:.2f}°")
            break

        # Small delay to avoid excessive updates
        time.sleep(0.1)


if __name__ == '__main__':
    capture(*sys.argv[1:])

