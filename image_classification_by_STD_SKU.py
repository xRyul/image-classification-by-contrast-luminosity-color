# CONTRAST ANALYSIS (based on std_dev) - SKU optimised
# E.g.: keep alss _01 _02 skus together

# Below code will process folder of images and categorise into subfolders
# based on 30 points of standard devation variance
# - This script converts images to grayscale before processing.
# - This script moves the original files into categorized folders.


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

# Constants
INTERVAL = 40
IMAGE_EXTENSIONS = ('.psd', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.tif', '.webp')

# Specify input and output folders here
INPUT_FOLDERS = ['/Users/dan00477/Desktop/untitled folder 2 2']
OUTPUT_FOLDER = '/Users/dan00477/Desktop/output'

# Flag to control whether to delete original files after categorization
DELETE_ORIGINALS = False

def clean_filename(filename):
    cleaned_filename = re.sub(r'\.\w+$', '', filename)
    cleaned_filename = re.sub(r"[^a-zA-Z0-9]", " ", cleaned_filename)
    cleaned_filename = re.sub(r"\D", " ", cleaned_filename)
    cleaned_filename = re.sub(r"\b\d{1,7}\b", " ", cleaned_filename)
    cleaned_filename = re.sub(r"\s+", " ", cleaned_filename).strip()
    return cleaned_filename.split()[0] if cleaned_filename else ""

def calculate_std_dev(filename):
    with Image.open(filename) as img:
        img_data = np.array(img.convert('L')).flatten()
    return np.std(img_data)

def process_image(filename):
    return clean_filename(filename), calculate_std_dev(filename)

def get_image_files(folder_path):
    return [
        os.path.join(folder_path, filename)
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(IMAGE_EXTENSIONS)
    ]

def categorize_image(filename, sku, avg_std_dev, output_folder):
    category = int(avg_std_dev // INTERVAL) * INTERVAL
    subfolder_path = os.path.join(output_folder, f"category-{category}-{category + INTERVAL - 1}")
    os.makedirs(subfolder_path, exist_ok=True)
    if sku in filename:
        if DELETE_ORIGINALS:
            shutil.move(filename, subfolder_path)
        else:
            shutil.copy2(filename, subfolder_path)

def categorize_images(input_folders, output_folder):
    for input_folder in input_folders:
        image_files = get_image_files(input_folder)
        
        with multiprocessing.Pool() as pool:
            results = pool.map(process_image, image_files)
        
        sku_std_devs = defaultdict(list)
        for sku, std_dev in results:
            sku_std_devs[sku].append(std_dev)
        
        for sku, std_devs in sku_std_devs.items():
            avg_std_dev = sum(std_devs) / len(std_devs)
            for filename in image_files:
                categorize_image(filename, sku, avg_std_dev, output_folder)
        
        print_category_counts(output_folder)

def print_category_counts(folder_path):
    for subfolder in os.listdir(folder_path):
        if subfolder.startswith("category-"):
            subfolder_path = os.path.join(folder_path, subfolder)
            image_count = len([f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))])
            print(f"{subfolder_path}: {image_count} images")

def main():
    start_time = time.time()
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    categorize_images(INPUT_FOLDERS, OUTPUT_FOLDER)
    
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")
    if DELETE_ORIGINALS:
        print("Original files have been moved to the categorized folders.")
    else:
        print("Original files have been kept in their original location.")

if __name__ == '__main__':
    main()