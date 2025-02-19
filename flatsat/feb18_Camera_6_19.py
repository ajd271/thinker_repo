# AUTHOR: 
# DATE:

# Import necessary libraries
import time
import board
import sys
import csv
import os
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2
from image_processor import *  # Import the function

# VARIABLES
THRESHOLD = 0.08  # Acceleration threshold for detecting a shake
REPO_PATH = "/home/pi/thinker_repo"  # GitHub repo path
FOLDER_PATH = "/flatsat"  # Folder where images are saved
CSV_FILE = f"{REPO_PATH}/{FOLDER_PATH}/brightness_data.csv"  # CSV file path
IMAGE_INTERVAL = 3  # Time (in seconds) between each photo

# Initialize IMU and Camera
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()

def setup_csv():
    """Create CSV file if it doesn't exist and add headers."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Image Filename", "Brightness Values"])  # Header row

def save_to_csv(image_path, brightness_values):
    """Save image brightness values to CSV."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, image_path, brightness_values])  # Save data

def git_push():
    """Push new images and CSV data to GitHub."""
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo and Brightness Data')
        origin.push()
        print('Uploaded images and CSV data to GitHub')
    except:
        print("Couldn't upload to GitHub")

def img_gen(name):
    """Generate a timestamped image filename."""
    t = time.strftime("_%H%M%S")
    return f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}.jpg'

def take_photos(duration):
    """Take multiple photos for the specified duration and save brightness data."""
    setup_csv()  # Ensure CSV is set up
    start_time = time.time()
    name = "ThinkerS"  # Replace with your name

    while time.time() - start_time < duration:
        accelx, accely, accelz = accel_gyro.acceleration
        
        if accelx > THRESHOLD or accely > THRESHOLD:
            time.sleep(2)  # Pause before capturing
            filename = img_gen(name)
            picam2.start_and_capture_file(filename)
            print(f"Photo saved: {filename}")

            # Analyze the photo
            brightness_values = calculate_average_light(filename)
            print(f"Brightness Values: {brightness_values}")

            # Save to CSV
            save_to_csv(filename, brightness_values)

        time.sleep(IMAGE_INTERVAL)  # Wait before taking another photo

    git_push()  # Push all images and CSV after capturing

def main():
    """Main function to get user input and start photo capture."""
    if len(sys.argv) < 2:
        print("Usage: python3 feb16camera.py <duration_in_seconds>")
        sys.exit(1)

    duration = int(sys.argv[1])
    print(f"Running for {duration} seconds...")
    take_photos(duration)

if __name__ == '__main__':
    main()
