import os
import time
import csv
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np
from picamera2 import Picamera2
from image_processor import calculate_average_light 
import subprocess  # For uploading to GitHub
from sensor_calc_V2 import *  # Import sensor functions

# Ensure the images folder exists
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(SCRIPT_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def get_timestamp():
    """Returns a timestamp string for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def capture_image(filename):
    """Captures an image and saves it to the specified filename."""
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)  # Allow camera to adjust
    picam2.capture_file(filename)
    picam2.close()


def compute_displacement(acceleration_data, time_interval):
    """Uses kinematic equations to compute displacement based on acceleration data."""
    velocity = 0
    displacement = 0
    for accel in acceleration_data:
        velocity += accel * time_interval
        displacement += velocity * time_interval + 0.5 * accel * (time_interval ** 2)
    return displacement


def analyze_brightness_blocks(image_path, threshold):
    """Analyzes brightness in 10x10 pixel blocks and returns a matrix indicating power outage areas."""
    image = Image.open(image_path).convert("L")
    width, height = image.size
    pixels = np.array(image)
    status_matrix = []
   
    for y in range(0, height, 10):
        row = []
        for x in range(0, width, 10):
            block = pixels[y:y+10, x:x+10]
            avg_brightness = np.mean(block)
            row.append(avg_brightness)
        status_matrix.append(row)
    return status_matrix

def save_brightness_to_csv(initial_matrix, second_matrix, csv_filename, threshold):
    """Saves block-wise brightness analysis to a CSV file with outage and restoration data."""
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Block Row", "Block Column", "Status"])
        for i, (row1, row2) in enumerate(zip(initial_matrix, second_matrix)):
            for j, (val1, val2) in enumerate(zip(row1, row2)):
                if val2 < threshold and val1 >= threshold:
                    status = "Outage"
                elif val2 >= threshold and val1 < threshold:
                    status = "Restored"
                else:
                    status = "Same"
                writer.writerow([i, j, status])

def overlay_outage_map(image_path, initial_matrix, second_matrix, threshold, output_path):
    """Creates an overlay image highlighting outages (red) and restorations (green)."""
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
   
    for y, (row1, row2) in enumerate(zip(initial_matrix, second_matrix)):
        for x, (val1, val2) in enumerate(zip(row1, row2)):
            if val2 < threshold and val1 >= threshold:
                draw.rectangle([(x*10, y*10), (x*10+10, y*10+10)], width=2, fill=(255, 0, 0, 100))
            elif val2 >= threshold and val1 < threshold:
                draw.rectangle([(x*10, y*10), (x*10+10, y*10+10)], width=2, fill=(0, 255, 0, 100))
   
    image.save(output_path)

def main():
    print("Initializing sensors...")
    calibrate_gyro()
    calibrate_mag()
    print("You can now place CubeSat on gantry")
    time.sleep(10)
   
    timestamp = get_timestamp()
    initial_image_path = os.path.join(IMAGE_DIR, f"initial_{timestamp}.jpg")
    capture_image(initial_image_path)
    print("Initial image captured. CubeSat can now be moved.")
   
    acceleration_data = []
    while True:
        acceleration_data.append(accel_gyro.acceleration[0])
        if len(acceleration_data) > 20:
            acceleration_data.pop(0)
        displacement = compute_displacement(acceleration_data, 0.1)
        if abs(displacement) > 1:
            print("CubeSat has traveled far enough")
            break
        time.sleep(0.1)
   
    while True:
        acceleration_data.append(accel_gyro.acceleration[0])  
        if len(acceleration_data) > 20:
            acceleration_data.pop(0)
        displacement = compute_displacement(acceleration_data, 0.1)
        if abs(displacement) < 0.3:
            print("CubeSat has returned to its original position. Capturing second image...")
            second_image_path = os.path.join(IMAGE_DIR, f"second_{timestamp}.jpg")
            capture_image(second_image_path)
            break
        time.sleep(0.1)
   
    BRIGHTNESS_THRESHOLD = 100  # Adjust based on expected conditions
    initial_brightness = analyze_brightness_blocks(initial_image_path, BRIGHTNESS_THRESHOLD)
    second_brightness = analyze_brightness_blocks(second_image_path, BRIGHTNESS_THRESHOLD)
   
    csv_filename = os.path.join(SCRIPT_DIR, f"brightness_diff_{timestamp}.csv")
    save_brightness_to_csv(initial_brightness, second_brightness, csv_filename, BRIGHTNESS_THRESHOLD)
   
    overlay_path = os.path.join(IMAGE_DIR, f"brightness_overlay_{timestamp}.jpg")
    overlay_outage_map(second_image_path, initial_brightness, second_brightness, BRIGHTNESS_THRESHOLD, overlay_path)
   
    subprocess.run(["git", "add", csv_filename, initial_image_path, second_image_path, overlay_path])
    subprocess.run(["git", "commit", "-m", "Updated brightness difference data"])
    subprocess.run(["git", "push"])
   
    print("Brightness analysis complete.")
   
if __name__ == "__main__":
    main()
