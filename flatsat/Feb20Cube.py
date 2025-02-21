import os
import time
import csv
from datetime import datetime
from PIL import Image
import numpy as np
from picamera2 import Picamera2
from image_processor import calculate_average_light  # Ensure this function exists
import subprocess  # For uploading to GitHub
from sensor_calc_V2 import *  # Import sensor functions

# Ensure the images folder exists
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def capture_image(filename):
    """Captures an image and saves it to the specified filename."""
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)  # Allow camera to adjust
    picam2.capture_file(filename)
    picam2.close()

def save_brightness_to_csv(brightness_array, csv_filename):
    """Saves brightness data to a CSV file."""
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Pixel Index", "Brightness Difference"])
        for i, brightness in enumerate(brightness_array):
            writer.writerow([i, brightness])

def compute_displacement(acceleration_data, time_interval):
    """Uses kinematic equations to compute displacement based on acceleration data."""
    velocity = 0
    displacement = 0
    for accel in acceleration_data:
        velocity += accel * time_interval
        displacement += velocity * time_interval + 0.5 * accel * (time_interval ** 2)
    return displacement

def main():
    print("Initializing sensors...")
    calibrate_gyro()
    calibrate_mag()
    print("You can now place cubesat on gantry")
    time.sleep(20)  # give time to place cubesat on gantrys

    initial_image_path = os.path.join(IMAGE_DIR, "initial.jpg")
    capture_image(initial_image_path)
    print("Initial image captured. CubeSat can now be moved.")
    acceleration_data = []
    start_time = time.time()
    #while time.time() - start_time <2:
        #acceleration_data.append(accel_gyro.acceleration[0])
        #time.sleep(0.1) 
    
    while True:
        acceleration_data.append(accel_gyro.acceleration[0]) 
        if len(acceleration_data) > 20:
            acceleration_data.pop(0)
        displacement = compute_displacement(acceleration_data, 0.1)
        if abs(displacement) > 1:  # Threshold for detecting return to start position
            print("CubeSat has travelled far enough")
            break
        time.sleep(0.1)
    while True:
        acceleration_data.append(accel_gyro.acceleration[0])  
        if len(acceleration_data) > 20:
            acceleration_data.pop(0)
        displacement = compute_displacement(acceleration_data, 0.1)
        if abs(displacement) < 0.5:  # Threshold for detecting return to start position
            print("CubeSat has returned to its original position. Capturing second image...")
            second_image_path = os.path.join(IMAGE_DIR, "second.jpg")
            capture_image(second_image_path)
            break
        time.sleep(0.1)
    
    # Analyze brightness differences
    initial_brightness = calculate_average_light(initial_image_path)
    second_brightness = calculate_average_light(second_image_path)
    brightness_diff = np.array(initial_brightness) - np.array(second_brightness)
    total_brightness_diff = np.sum(abs(brightness_diff))
    
    # Save to CSV
    csv_filename = os.path.join(SCRIPT_DIR, "brightness_diff.csv")
    save_brightness_to_csv(brightness_diff, csv_filename)
    
    # Generate grayscale image from brightness difference
    diff_image = Image.fromarray(np.uint8(np.clip(brightness_diff, 0, 255)))
    diff_image.save(os.path.join(IMAGE_DIR, "brightness_diff.jpg"))
    
    # Upload to GitHub (assuming script is configured for GitHub upload)
    subprocess.run(["git", "add", csv_filename])
    subprocess.run(["git", "commit", "-m", "Updated brightness difference data"]) 
    subprocess.run(["git", "push"])
    
    # Threshold check for power outage
    BRIGHTNESS_THRESHOLD = 500000  # Adjust based on expected conditions
    if total_brightness_diff > BRIGHTNESS_THRESHOLD:
        print("Significant brightness change detected: Potential power outage.")
    else:
        print("Brightness difference within normal range.")

if __name__ == "__main__":
    main()
