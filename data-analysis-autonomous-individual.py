# Below code will process folder of images and categorise into subfolders
# based on 10 points of standard devation variance

# - Regardless of filename

# Adjust "interval" value as needed.
# - the lower the number then small the variance, the more folders will be created
# - the higher the number the bigger the variance, the less folders will be created

import numpy as np
import os
from PIL import Image
import multiprocessing
import time
import shutil

def calculate_std_dev(filename):
    # Open the image file
    with Image.open(filename) as img:
        # Convert the image to grayscale
        img = img.convert('L')
        # Convert the image data to a numpy array
        img_data = np.array(img)
        # Flatten the image data
        img_data_flattened = img_data.flatten()

    std_dev = np.std(img_data_flattened)

    return std_dev

def categorize_psd_images(folders):
    # Initialize a list to store standard deviations
    std_devs = []

    for folder_path in folders:
        # Get a list of all image files in the folder
        image_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith(('.psd', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.tif', '.webp'))]

        # Create a multiprocessing Pool
        pool = multiprocessing.Pool()

        # Process the images in parallel
        results = pool.map(calculate_std_dev, image_files)

        # Close the pool
        pool.close()
        pool.join()

        # Add the results to the list
        std_devs.extend(results)

        # Calculate the minimum and maximum standard deviation
        min_std_dev = min(std_devs)
        max_std_dev = max(std_devs)

        # Calculate the interval
        interval = 30

        # Create the subfolders if they don't exist and move the image files to the subfolders
        for filename, std_dev in zip(image_files, std_devs):
            # Determine the category based on the standard deviation
            category = int(std_dev // interval) * interval
            # Create the subfolder if it doesn't exist
            subfolder_path = os.path.join(folder_path, f"category-{category}-{category + interval - 1}")
            os.makedirs(subfolder_path, exist_ok=True)
            # Move the image file to the subfolder
            shutil.move(filename, subfolder_path)

        # Print the number of images in each category
        for i in range(int(min_std_dev // interval), int(max_std_dev // interval) + 1):
            subfolder_path = os.path.join(folder_path, f"category-{i * interval}-{i * interval + interval - 1}")
            if os.path.exists(subfolder_path):
                print(f"{subfolder_path}: {len(os.listdir(subfolder_path))} images")

# Call the function
if __name__ == '__main__':
    # Start the timer
    start_time = time.time()

    # Call the function
    folders = ['/Users/dan00477/Desktop/2_files']
    categorize_psd_images(folders)

    # Print the total execution time
    print(f"Total execution time: {time.time() - start_time} seconds")
