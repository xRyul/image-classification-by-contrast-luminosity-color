# Below code will process folder of images and categorise into subfolders
# based on 10 points of standard devation variance

# THIS is OPTIMIZED FOR SKUs e.g.: 12345678_01.jpg, 12345678_02.jpg
# so that iamges would be moved in sets/groups! 

# Adjust "interval" value as needed.
# - the lower the number then small the variance, the more folders will be created
# - the higher the number the bigger the variance, the less folders will be created

import numpy as np
import os
import re
from collections import defaultdict
from PIL import Image
import multiprocessing
import time
import shutil


def clean_filename(filename):
    # Remove file extension
    cleaned_filename = re.sub(r'\.\w+$', '', filename)
    # Remove non alphabetic characters
    cleaned_filename = re.sub(r"[^a-zA-Z0-9]", " ", cleaned_filename)
    # Remove any words or letters
    cleaned_filename = re.sub(r"\D", " ", cleaned_filename)
    # Remove any sequences of digits that are less than 8 digits long
    cleaned_filename = re.sub(r"\b\d{1,7}\b", " ", cleaned_filename)
    # Replace all whitespace or empty space with single space
    cleaned_filename = re.sub(r"\s+", " ", cleaned_filename)
    # Remove any leading whitespace
    cleaned_filename = cleaned_filename.lstrip()

    # Extract the SKU from the cleaned filename
    sku = cleaned_filename.split(' ')[0]

    return sku


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


def process_image(filename):
    sku = clean_filename(filename)
    std_dev = calculate_std_dev(filename)
    return sku, std_dev



def categorize_psd_images(folders):
    # Initialize dictionaries to store SKU counts and files
    sku_std_devs = defaultdict(list)

    for folder_path in folders:
        # Get a list of all image files in the folder
        image_files = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith(('.psd', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.tif', '.webp'))]

        # Create a multiprocessing Pool
        pool = multiprocessing.Pool()

        # Process the images in parallel
        results = pool.map(process_image, image_files)

        # Close the pool
        pool.close()
        pool.join()

        # Add the results to the dictionary
        for sku, std_dev in results:
            sku_std_devs[sku].append(std_dev)

        # Now calculate the average standard deviation for each SKU and print the categorization result
        std_dev_values = []
        for sku, std_devs in sku_std_devs.items():
            avg_std_dev = sum(std_devs) / len(std_devs)
            std_dev_values.append(avg_std_dev)

        # Calculate the minimum and maximum standard deviation
        min_std_dev = min(std_dev_values)
        max_std_dev = max(std_dev_values)

        # Calculate the interval
        interval = 40

        # Create the subfolders if they don't exist and move the image files to the subfolders
        for sku, std_devs in sku_std_devs.items():
            avg_std_dev = sum(std_devs) / len(std_devs)
            for filename in image_files:
                if sku in filename:
                    # Determine the category based on the average standard deviation
                    category = int(avg_std_dev // interval) * interval
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
