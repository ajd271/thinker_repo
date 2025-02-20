# AUTHOR: 
# DATE:

# Import necessary libraries
import time
import board
import sys
import csv
import os
import numpy as np
from PIL import Image
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2
from feb16camera import calculate_average_light  # Import brightness function

# VARIABLES
THRESHOLD = 0.08  # Acceleration threshold
REPO_PATH = "/home/pi/thinker_repo"
FOLDER_PATH = "/flatsat/images"  # Now stores everything in 'images' folder
CSV_FILE = f"{REPO_PATH}/{FOLDER_PATH}/brightness_data.csv"
IMAGE_INTERVAL = 3  # Time (in seconds) between each photo
BLOCK_SIZE = 10  # Grid size for brightness processing

# Ensure the images directory exists
os.makedirs(REPO_PATH + FOLDER_PATH, exist_ok=True)

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
            writer.writerow(["Timestamp", "Image Filename", "Brightness Filename", "Brightness Values"])

def save_to_csv(image_path, brightness_image_path, brightness_values):
    """Save image brightness values to CSV."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, image_path, brightness_image_path, brightness_values])

def git_push():
    """Push new images and CSV data to GitHub."""
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo, Brightness Data, and Grayscale Image')
        origin.push()
        print('Uploaded images, grayscale JPG, and CSV data to GitHub')
    except:
        print("Couldn't upload to GitHub")

def img_gen(name, suffix=""):
    """Generate a timestamped filename inside images folder."""
    t = time.strftime("_%H%M%S")
    return f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}{suffix}.jpg'

def generate_grayscale_image(brightness_values, filename):
    """Create a grayscale image using brightness values."""
    size = int(np.sqrt(len(brightness_values)))  # Assuming square grid
    image_data = np.array(brightness_values, dtype=np.uint8).reshape((size, size))
    img = Image.fromarray(image_data, mode='L')  # Convert array to grayscale image
    img.save(filename)
    print(f"Grayscale image saved: {filename}")

def take_photos(duration):
    """Take multiple photos for the specified duration and save brightness data."""
    setup_csv()
    start_time = time.time()
    name = "ThinkerS"

    while time.time() - start_time < duration:
        accelx, accely, accelz = accel_gyro.acceleration
        
        if accelx > THRESHOLD or accely > THRESHOLD:
            time.sleep(2)  # Pause before capturing
            image_filename = img_gen(name)
            picam2.start_and_capture_file(image_filename)
            print(f"Photo saved: {image_filename}")

            # Analyze brightness
            brightness_values = calculate_average_light(image_filename, BLOCK_SIZE)
            print(f"Brightness Values: {brightness_values}")

            # Create grayscale image
            grayscale_filename = img_gen(name, "_grayscale")
            generate_grayscale_image(brightness_values, grayscale_filename)

            # Save to CSV
            save_to_csv(image_filename, grayscale_filename, brightness_values)

        time.sleep(IMAGE_INTERVAL)  # Wait before taking another photo

    git_push()

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
