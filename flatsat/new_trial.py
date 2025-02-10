# Import libraries
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
import time
import os
import board
import busio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from multiprocessing import Process, Event
from picamera2 import Picamera2
import numpy as np

# IMU Initialization
i2c = busio.I2C(board.SCL, board.SDA)
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()

# Graphing Setup
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs, y1, y2, y3 = [], [], [], []
THRESHOLD = 0.02  # Adjust this value if needed
stop_event = Event()  # Global stop event for clean shutdown

# Animation function
def animate(i, xs, y1, y2, y3, mag_offset, gyro_offset, initial_angle):
    if not y1:
        prev_ang = initial_angle
    else:
        prev_ang = [y1[-1], y2[-1], y3[-1]]

    accelX, accelY, accelZ = accel_gyro.acceleration
    magX, magY, magZ = mag.magnetic
    magX -= mag_offset[0]
    magY -= mag_offset[1]
    magZ -= mag_offset[2]

    gyroX, gyroY, gyroZ = accel_gyro.gyro
    gyroX = gyroX * (180 / np.pi) - gyro_offset[0]
    gyroY = gyroY * (180 / np.pi) - gyro_offset[1]
    gyroZ = gyroZ * (180 / np.pi) - gyro_offset[2]

    xs.append(time.time())

    # Use accelerometer and magnetometer
    y1.append(roll_am(accelX, accelY, accelZ))
    y2.append(pitch_am(accelX, accelY, accelZ))
    y3.append(yaw_am(accelX, accelY, accelZ, magX, magY, magZ))

    ax.clear()
    ax.plot(xs, y1, label="Roll")
    ax.plot(xs, y2, label="Pitch")
    ax.plot(xs, y3, label="Yaw")
    plt.title('Roll, Pitch, Yaw using Accelerometer & Magnetometer')
    plt.ylabel('Degrees')
    plt.xlabel('Time')
    plt.legend()
    plt.grid()

    xs, y1, y2, y3 = xs[-20:], y1[-20:], y2[-20:], y3[-20:]  # Keep recent 20 values

# Function to run the plot
def plot_data():
    mag_offset = calibrate_mag()
    initial_angle = set_initial(mag_offset)
    gyro_offset = calibrate_gyro()
   
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, y1, y2, y3, mag_offset, gyro_offset, initial_angle), interval=1000)
   
    print("Starting graph plotting...")
    plt.show()

# Function to take photos based on acceleration threshold
def take_photo():
    print("Photo process started!")  # Debugging

    while not stop_event.is_set():
        accelx, accely, accelz = accel_gyro.acceleration
        print(f"Accel Data: X={accelx}, Y={accely}, Z={accelz}, Threshold={THRESHOLD}")  # Debugging
       
        if accelx > THRESHOLD and accely > THRESHOLD:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            time.sleep(2)  # Pause before taking the photo
            picam2.start_and_capture_file(filename)
            print(f"Photo saved successfully as {filename}!")

        time.sleep(0.5)  # Prevent CPU overload

# Main execution
if __name__ == '__main__':
    try:
        # Start both processes
        photo_process = Process(target=take_photo)
        plot_process = Process(target=plot_data)

        photo_process.start()
        plot_process.start()

        # Keep running until interrupted
        photo_process.join()
        plot_process.join()

    except KeyboardInterrupt:
        print("\nStopping processes...")

        # Signal processes to stop
        stop_event.set()
       
        photo_process.terminate()  # Force stop photo process
        plot_process.terminate()   # Force stop plot process
       
        photo_process.join()
        plot_process.join()

        print("All processes stopped successfully.")



