"""
The Python code you will write for this module should read
acceleration data from the IMU. When a reading comes in that surpasses
an acceleration threshold (indicating a shake), your Pi should pause,
trigger the camera to take a picture, then save the image with a
descriptive filename. You may use GitHub to upload your images automatically,
but for this activity it is not required.

The provided functions are only for reference, you do not need to use them. 
You will need to complete the take_photo() function and configure the VARIABLES section
"""

#AUTHOR: 
#DATE:

#import libraries
import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2

#VARIABLES
THRESHOLD = 0.002      #Any desired value from the accelerometer
REPO_PATH = "/home/pi/thinker_repo"     #Your github repo path: ex. /home/pi/FlatSatChallenge
FOLDER_PATH = "/flatsat"   #Your image folder path in your GitHub repo: ex. /Images

#imu and camera initialization
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
        print('added remote')
        origin.pull()
        print('pulled changes')
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        print('made the commit')
        origin.push()
        print('pushed changes')
    except:
        print('Couldn\'t upload to git')


def img_gen(name):
    """
    This function is complete. Generates a new image name.

    Parameters:
        name (str): your name ex. MasonM
    """
    t = time.strftime("_%H%M%S")
    imgname = (f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}.jpg')
    return imgname


def take_photo():

    while True:
        accelx, accely, accelz = accel_gyro.acceleration
        
        if accelx>THRESHOLD and accely>THRESHOLD:
        #CHECKS IF READINGS ARE ABOVE THRESHOLD
            time.sleep(2) #PAUSE
            name = "ThinkerS"     #First Name, Last Initial  ex. MasonM
            picam2.start_and_capture_file(filename)
            git_push()
            print("Photo saved successfully") 
            

def main():
    take_photo()


if __name__ == '__main__':
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"photo_{timestamp}.jpg"
    main()
    
