"""

This script processes a directory of images, analyzes their attributes (luminosity, 
color, and standard deviation), then categorizes them into subdirectories based on 
these attributes.

Key features:
- Analyzes image luminosity, average color (hue), and pixel value standard deviation
- Categorizes images into subdirectories based on luminosity, hue, and standard deviation ranges
- Offers optional recursive directory scanning

Usage:
Modify the input_folder, output_folder, and other parameters before running the script.

ability to find all PINK images from the batch of 100,000.
Or find all Black and white images from the set of all color images etc.

Sample Output Example:
Let's assume we set the following parameters:

hue_variance = 40
std_variance = 40
input_folder contains 1000 images

test-data/
├── Luminosity/
│   ├── 0-24/
│   ├── 25-49/
│   ├── 50-74/
│   ├── 75-99/
│   ├── 100-124/
│   ├── 125-149/
│   ├── 150-174/
│   ├── 175-199/
│   ├── 200-224/
│   └── 225-249/
├── std/
│   ├── 0-39/
│   ├── 40-79/
│   ├── 80-119/
│   └── 120-159/
└── hue/
    ├── 0-39/
    ├── 40-79/
    ├── 80-119/
    ├── 120-159/
    ├── 160-199/
    ├── 200-239/
    ├── 240-279/
    ├── 280-319/
    └── 320-359/

Each subdirectory would contain copies of the images that fall into that category.

"""


import os
import time
import shutil
import colorsys
from multiprocessing import Pool
import numpy as np
from PIL import Image

# Configuration constants
INPUT_FOLDER = "/Users/dan00477/Desktop/untitled folder 2 2"
OUTPUT_FOLDER = "/Users/dan00477/Desktop/output"
RECURSIVE = True
DELETE_ORIGINALS = False

# Categorization intervals
LUMINOSITY_INTERVAL = 60
HUE_INTERVAL = 10
STD_INTERVAL = 60

# File extensions to process
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.psd', '.tif', '.tiff')

def process_image(path):
    try:
        with Image.open(path) as img:
            # Convert image to RGBA if it's not already
            img = img.convert('RGBA')

            # Create a white background
            background = Image.new('RGBA', img.size, (255, 255, 255))
            
            # Composite the image onto the white background
            composite = Image.alpha_composite(background, img)
            
            # Convert to RGB for further processing
            rgb_img = composite.convert('RGB')
            
            img_data = np.array(rgb_img)
            
            # Remove alpha channel if present
            if img_data.shape[2] == 4:
                img_data = img_data[:, :, :3]

            # Calculate luminosity
            # (0.299, 0.587, and 0.114) are coefficients used in a standard formula 
            # for calculating the luminosity or perceived brightness of a color.
            # The coefficients:
                # 0.299 for Red
                # 0.587 for Green
                # 0.114 for Blue
            # using NumPy's dot product function to efficiently apply this formula 
            # to every pixel in the image. The img_data[..., :3] selects all pixels 
            # and their RGB values, and the dot product with [0.299, 0.587, 0.114] 
            # applies the luminosity formula to each pixel.
            luminosity = np.dot(img_data[..., :3], [0.299, 0.587, 0.114])
            avg_luminosity = np.mean(luminosity)
            
            std_dev = np.std(img_data)
            
            img_data_normalized = img_data.astype(np.float32) / 255
            avg_color = np.mean(img_data_normalized, axis=(0, 1))
            
            try:
                h, _, _ = colorsys.rgb_to_hls(*avg_color)
                color_category = int(h * 360)
            except ValueError:
                color_category = None
            
            return path, avg_luminosity, std_dev, color_category
    except Exception as e:
        print(f"Failed to process {path}, error: {e}")
        return None

def get_image_paths(folder_path, recursive=True):
    image_paths = []
    
    for root, _, files in os.walk(folder_path):
        image_paths.extend(
            os.path.join(root, file)
            for file in files
            if file.lower().endswith(IMAGE_EXTENSIONS)
        )
        if not recursive:
            break

    return image_paths

def process_directory(folder_path, recursive=True):
    image_paths = get_image_paths(folder_path, recursive)

    with Pool() as pool:
        results = pool.map(process_image, image_paths)

    return [result for result in results if result is not None]

def categorize_image(path, luminosity, std, color_category, output_folder):
    luminosity_category = (luminosity // LUMINOSITY_INTERVAL) * LUMINOSITY_INTERVAL
    std_category = (std // STD_INTERVAL) * STD_INTERVAL
    hue_category = (color_category // HUE_INTERVAL) * HUE_INTERVAL if color_category is not None else None
    
    subfolders = {
        "Luminosity": f"{luminosity_category}-{luminosity_category + LUMINOSITY_INTERVAL - 1}",
        "std": f"{std_category}-{std_category + STD_INTERVAL - 1}",
        "hue": f"{hue_category}-{hue_category + HUE_INTERVAL - 1}" if hue_category is not None else "Unknown"
    }

    for category, subfolder in subfolders.items():
        full_path = os.path.join(output_folder, category, subfolder)
        os.makedirs(full_path, exist_ok=True)
        if DELETE_ORIGINALS:
            shutil.move(path, full_path)
        else:
            shutil.copy(path, full_path)

def categorize_and_copy_images(results, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for result in results:
        if result is not None:
            path, luminosity, std, color_category = result
            categorize_image(path, luminosity, std, color_category, output_folder)

def main():
    start_time = time.time()

    results = process_directory(INPUT_FOLDER, recursive=RECURSIVE)
    categorize_and_copy_images(results, OUTPUT_FOLDER)

    duration = time.time() - start_time
    print(f"Processing completed in {duration:.2f} seconds")
    print(f"{'Moved' if DELETE_ORIGINALS else 'Copied'} images to {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()