import os
import time
import csv
from datetime import datetime
from PIL import Image
import numpy as np
from picamera2 import Picamera2  # Ensure you have this installed
from image_processor import calculate_average_light  # Import your function
import subprocess  # For uploading to GitHub
from sensor_calc_V2 import *

# Ensure the images folder exists
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current script's directory
IMAGE_DIR = os.path.join(SCRIPT_DIR, "images")  # Ensure we use the existing images folder
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
        writer.writerows(brightness_array)

def generate_grayscale_image(brightness_array, image_filename):
    """Creates and saves a grayscale image based on brightness data."""
    brightness_array = np.array(brightness_array)  # Ensure it's a NumPy array
    img = Image.fromarray(brightness_array.astype(np.uint8), mode='L')
    img.save(image_filename)

def upload_to_github(image_path, csv_path):
    """Uploads the grayscale image and CSV file to GitHub."""
    try:
        subprocess.run(["git", "add", image_path, csv_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Added image & CSV: {os.path.basename(image_path)}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Files uploaded to GitHub successfully!")
    except subprocess.CalledProcessError:
        print("⚠ Error uploading to GitHub. Check your repo setup.")

def main():
    """Main function to take photos and process brightness."""
    duration = int(input("Enter the duration for image capture (in seconds): "))
    start_time = time.time()
   
    while time.time() - start_time < duration:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = os.path.join(IMAGE_DIR, f"image_{timestamp}.jpg")
        csv_path = os.path.join(IMAGE_DIR, f"brightness_{timestamp}.csv")
        grayscale_path = os.path.join(IMAGE_DIR, f"grayscale_{timestamp}.jpg")

        # Capture image
        capture_image(image_path)
        print(f"📸 Image saved: {image_path}")

        # Process brightness
        brightness_array = calculate_average_light(image_path)
        save_brightness_to_csv(brightness_array, csv_path)
        print(f"📊 Brightness CSV saved: {csv_path}")

        # Generate grayscale image
        generate_grayscale_image(brightness_array, grayscale_path)
        print(f"🖼 Grayscale image saved: {grayscale_path}")

        # Upload to GitHub
        upload_to_github(grayscale_path, csv_path, image_path)

        time.sleep(2)  # Small delay between captures

if __name__ == "__main__":
    main()
