# Below code is slow
# - It uses old method of opening files and only then calculating std dev
# - it will create sub-folders for variosu contrast levels

import os
import shutil
from psd_tools import PSDImage
import numpy as np
import logging
import warnings

# Warning/error supressiong e.g.: Unknown key: b'GenI', b'CAI ', b'OCIO' etc...
warnings.filterwarnings("ignore")
logging.getLogger('psd_tools').setLevel(logging.ERROR) 

def categorize_psd_images(folder_path):
    # Create subfolders if they don't exist
    if not os.path.exists(os.path.join(folder_path, 'Low Contrast')):
        os.makedirs(os.path.join(folder_path, 'Low Contrast'))
    if not os.path.exists(os.path.join(folder_path, 'High Contrast')):
        os.makedirs(os.path.join(folder_path, 'High Contrast'))
    if not os.path.exists(os.path.join(folder_path, 'Medium Contrast')):
        os.makedirs(os.path.join(folder_path, 'Medium Contrast'))

    for filename in os.listdir(folder_path):
        if filename.endswith(".psd"):
            # Load the PSD file
            psd = PSDImage.open(os.path.join(folder_path, filename))
            
            # Flatten the image
            flattened = psd.composite()
            
            # Convert the image to grayscale
            grayscale = flattened.convert('L')
            
            # Calculate standard deviation
            std_dev = np.std(np.array(grayscale))
            print(std_dev)  # Print the standard deviation for debugging
            
            # Move image to appropriate folder
            if std_dev <= 30:
                shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, 'Low Contrast', filename))
            elif std_dev >= 70:
                shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, 'High Contrast', filename))
            else:
                shutil.move(os.path.join(folder_path, filename), os.path.join(folder_path, 'Medium Contrast', filename))

# Call the function
categorize_psd_images('/Users/dan00477/Desktop/2_files')
