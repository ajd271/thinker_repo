# Import libraries
import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2
from image_processor.py import *
# VARIABLES
THRESHOLD = 0.08      # Any desired value from the accelerometer
REPO_PATH = "/home/pi/thinker_repo"  # Your GitHub repo path
FOLDER_PATH = "/flatsat"  # Image folder path in your GitHub repo
NUM_PHOTOS = 3  # Number of photos to take per shake event
PHOTO_INTERVAL = 1  # Seconds between photos
# IMU and camera initialization
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()

def git_push():
    """
    This function is complete. Stages, commits, and pushes new images to your GitHub repo.
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        origin.push()
        print('Photos uploaded to GitHub.')
    except Exception as e:
        print(f'Git upload failed: {e}')

def img_gen(name, count):
    """
    Generates a new image name.

    Parameters:
        name (str): User-defined identifier (e.g., "ThinkerS")
        count (int): Photo sequence number
    """
    t = time.strftime("_%H%M%S")
    return f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}_{count}.jpg'

def take_photo():
    """
    Captures multiple images when acceleration exceeds the threshold.
    """
    picam2.start(show_preview=False)  # Prevent DRM error in SSH

    while True:
        accelx, accely, accelz = accel_gyro.acceleration

        if accelx > THRESHOLD and accely > THRESHOLD:
            print("Shake detected! Capturing images...")
            time.sleep(2)  # Pause before taking photos
           
            name = "ThinkerS"  # First Name, Last Initial
            for i in range(NUM_PHOTOS):
                filename = img_gen(name, i + 1)
                picam2.capture_file(filename)
                print(f"Photo {i+1} saved: {filename}")
                time.sleep(PHOTO_INTERVAL)  # Wait between captures

            git_push()

def main():
    take_photo()

if __name__ == '__main__':
    main()
