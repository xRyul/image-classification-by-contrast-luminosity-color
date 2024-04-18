# 1. ALL filenames with the same SKU are put into set
# 2. Each set is then analysed for contrast: Low, Medium, High 85++
#   - This allows to keep all images together e.g.: _01 will not be seperated from _02 and _03 
# 3. Show output inCLI

import numpy as np
import os
import re
from collections import defaultdict
from PIL import Image
import multiprocessing
import time


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
    try:
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
    except OSError:
        print(f"Skipping broken file: {filename}")
        return None


def process_image(filename):
    sku = clean_filename(filename)
    std_dev = calculate_std_dev(filename)
    if std_dev is not None:
        return sku, std_dev
    else:
        return None, None

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
            if sku is not None and std_dev is not None:
                sku_std_devs[sku].append(std_dev)

        # Now calculate the average standard deviation for each SKU and print the categorization result
        low_contrast = 0
        medium_contrast = 0
        high_contrast = 0
        for sku, std_devs in sku_std_devs.items():
            avg_std_dev = sum(std_devs) / len(std_devs)
            if avg_std_dev <= 40:
                low_contrast += 1
            elif avg_std_dev >= 85:
                high_contrast += 1
            else:
                medium_contrast += 1

        print(f"{folder_path}: {low_contrast} Low Contrast, {medium_contrast} Medium Contrast, {high_contrast} High Contrast")

# Call the function
if __name__ == '__main__':
    # Start the timer
    start_time = time.time()

    # Call the function
    folders = ['/Volumes/Hams Hall Workspace/R2_StyleShoot1_WIP']
    categorize_psd_images(folders)

    # Print the total execution time
    print(f"Total execution time: {time.time() - start_time} seconds")
