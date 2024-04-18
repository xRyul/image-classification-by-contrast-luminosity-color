import os
import numpy as np
import time
from PIL import Image
from multiprocessing import Pool
import shutil

def process_image(path):
    try:
        with Image.open(path) as img:
            img_data = np.array(img)
            img_data = img_data.astype(np.float32)
            
            # Calculate luminosity
            luminosity = 0.299 * img_data[:, :, 0] + 0.587 * img_data[:, :, 1] + 0.114 * img_data[:, :, 2]
            avg_luminosity = np.mean(luminosity)
            
            # Flatten the image data to calculate the standard deviation across all channels
            flattened_data = img_data.flatten()
            std_dev = np.std(flattened_data)
            
            return path, avg_luminosity, std_dev
    except Exception as e:
        print(f"Failed to process {path}, error: {e}")
        return None, None, None

def process_directory(folder_path):
    image_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.psd', '.tif', '.tiff')):
                image_paths.append(os.path.join(root, file))

    with Pool() as pool:
        results = pool.map(process_image, image_paths)
    
    # Filter out None results (failed images)
    results = [result for result in results if result is not None]
    
    return results

def categorize_and_copy_images(results, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    luminosity_ranges = np.arange(0, 256, 25) # Adjusted for 0-255 range
    
    for path, luminosity, std in results:
        # Corrected condition to ensure it matches the range
        luminosity_category = next((range for range in luminosity_ranges if luminosity >= range and luminosity < range + 25), None)
        if luminosity_category is None:
            print(f"Luminosity value {luminosity} for image {path} is out of expected range. Skipping this image.")
            continue
        
        luminosity_subfolder = f"{output_folder}/Luminosity/{luminosity_category}-{luminosity_category + 24}"
        
        # Dynamically create std subfolders in 10-point variances
        std_category = int(std // 10) * 10
        std_subfolder = f"{output_folder}/std/{std_category}-{std_category + 9}"
        
        os.makedirs(luminosity_subfolder, exist_ok=True)
        os.makedirs(std_subfolder, exist_ok=True)
        
        shutil.copy(path, luminosity_subfolder)
        shutil.copy(path, std_subfolder)

def main():
    start = time.time()
    results = process_directory("c:/Users/Daniel/Desktop/WIP/00_Overtime/2024-03-27 DA/")
    duration = time.time() - start
    print(f"Time elapsed in processing images is: {duration} seconds")
    
    output_folder = "~/Desktop/test-data"
    categorize_and_copy_images(results, output_folder)

if __name__ == "__main__":
    main()
