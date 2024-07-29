# CONTRAST ANALYSIS (based on std_dev) - single images

# Below code will process folder of images and categorise into subfolders
# based on 30 points of standard devation variance. 

# - This script converts images to grayscale before processing.
# - This script COPIES the original files into categorized folders.

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
    try:
        with Image.open(filename) as img:
            img = img.convert('L')
            img_data = np.array(img)
            return filename, np.std(img_data)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return filename, None

def categorize_images(input_folder, output_folder, interval=30):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = [
        os.path.join(input_folder, filename) 
        for filename in os.listdir(input_folder) 
        if filename.lower().endswith(('.psd', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.tif', '.webp'))
    ]

    # Use all available CPU cores
    with multiprocessing.Pool() as pool:
        results = pool.map(calculate_std_dev, image_files)

    categories = {}
    for filename, std_dev in results:
        if std_dev is not None:
            category = int(std_dev // interval) * interval
            category_name = f"category-{category}-{category + interval - 1}"
            if category_name not in categories:
                categories[category_name] = []
            categories[category_name].append(filename)

    for category, files in categories.items():
        subfolder_path = os.path.join(output_folder, category)
        os.makedirs(subfolder_path, exist_ok=True)
        for file in files:
            shutil.copy2(file, subfolder_path)
        print(f"{category}: {len(files)} images")

def main():
    # Configuration
    input_folder = "/Users/dan00477/Desktop/untitled folder 2 2"
    output_folder = "./data-output"
    interval = 30

    start_time = time.time()
    categorize_images(input_folder, output_folder, interval)
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    main()