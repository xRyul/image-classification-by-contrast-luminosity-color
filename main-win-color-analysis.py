import os
import numpy as np
import time
from PIL import Image
from multiprocessing import Pool
import shutil
import colorsys
from collections import Counter

def process_image(path):
    try:
        with Image.open(path) as img:
            img_data = np.array(img)
            
            # Check if the image has an alpha channel
            if img_data.shape[2] == 4:
                # Remove the alpha channel
                img_data = img_data[:, :, :3]
            
            # Calculate luminosity
            luminosity = 0.299 * img_data[:, :, 0] + 0.587 * img_data[:, :, 1] + 0.114 * img_data[:, :, 2]
            avg_luminosity = np.mean(luminosity)
            
            # Flatten the image data to calculate the standard deviation across all channels
            flattened_data = img_data.flatten()
            std_dev = np.std(flattened_data)
            print(std_dev)

            # Calculate average color
            img_data = img_data.astype(np.float32) / 255  # Normalize to 0-1
            avg_color = np.mean(img_data, axis=(0, 1))
            try:
                h, l, s = colorsys.rgb_to_hls(*avg_color)
                color_category = int(h * 360)  # Convert hue to a category between 0 and 359
            except ValueError:
                # Handle the case where the average color is not a valid RGB value
                color_category = None
            
            return path, avg_luminosity, std_dev, color_category
    except Exception as e:
        print(f"Failed to process {path}, error: {e}")
        return None, None, None, None

def process_directory(folder_path, recursive=True):
    image_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.psd', '.tif', '.tiff')):
                image_paths.append(os.path.join(root, file))
        if not recursive:
            break
    
    with Pool() as pool:
        results = pool.map(process_image, image_paths)
    
    # Filter out None results (failed images)
    results = [result for result in results if result is not None]
    
    
    return results

def categorize_and_copy_images(results, output_folder, hue_variance=40, std_variance=40):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    luminosity_ranges = np.arange(0, 256, 25) # Adjusted for 0-255 range

    # Find the unique hue categories based on the specified variance
    hue_categories = list(range(0, 361, hue_variance))
    color_categories = [f"{category}-{category + hue_variance - 1}" for category in hue_categories]

    for path, luminosity, std, color_category in results:
        # Corrected condition to ensure it matches the range
        luminosity_category = next((range for range in luminosity_ranges if luminosity >= range and luminosity < range + 25), None)
        if luminosity_category is None:
            print(f"Luminosity value {luminosity} for image {path} is out of expected range. Skipping this image.")
            continue
        
        luminosity_subfolder = f"{output_folder}/Luminosity/{luminosity_category}-{luminosity_category + 24}"

        # Adjusted std category calculation to use std_variance of 40
        std_category = int(std // std_variance) * std_variance
        std_subfolder = f"{output_folder}/std/{std_category}-{std_category + std_variance - 1}"

        # Determine the color category based on the hue value
        for i, category in enumerate(hue_categories):
            if color_category >= category and color_category < category + hue_variance:
                color_subfolder = f"{output_folder}/color/{color_categories[i]}"
                break
        else:
            print(f"Hue value {color_category} for image {path} is out of expected range. Skipping this image.")
            continue

        os.makedirs(color_subfolder, exist_ok=True)
        os.makedirs(luminosity_subfolder, exist_ok=True)
        os.makedirs(std_subfolder, exist_ok=True)

        shutil.copy(path, color_subfolder)
        shutil.copy(path, luminosity_subfolder)
        shutil.copy(path, std_subfolder)

def main():
    start = time.time()
    recursive = True  # Set to False to disable recursive search
    results = process_directory("c:/Users/Daniel/Desktop/WIP/00_Overtime/2024-03-27 DA/", recursive=recursive)
    duration = time.time() - start
    print(f"Time elapsed in processing images is: {duration} seconds")
    
    output_folder = "~/Desktop/test-data"
    categorize_and_copy_images(results, output_folder, hue_variance=40, std_variance=40)


if __name__ == "__main__":
    main()