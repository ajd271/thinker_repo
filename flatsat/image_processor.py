from PIL import Image
import numpy as np

def calculate_average_light(image_path, block_size=10):
    # Open the image
    image = Image.open(image_path).convert('L')  # Convert to grayscale
   
    # Convert image to numpy array
    img_array = np.array(image)
   
    # Get image dimensions
    height, width = img_array.shape
   
    # Store the average brightness values
    brightness_values = []
   
    # Iterate over the image in block_size steps
    for y in range(0, height, block_size):
        row = []
        for x in range(0, width, block_size):
            # Extract block
            block = img_array[y:y+block_size, x:x+block_size]
           
            # Calculate average brightness of the block
            avg_brightness = np.mean(block)
            row.append(avg_brightness)
        brightness_values.append(row)
    return np.array(brightness_values)


# Example usage
if __name__ == "__main__":
    image_path = "your_image.jpg"  # Change this to your image path
    brightness_data = calculate_average_light(image_path)
   
    for position, brightness in brightness_data:
        print(f"Block at {position}: Average brightness = {brightness:.2f}")
