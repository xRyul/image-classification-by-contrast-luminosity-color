# Image Classification based on contrast, luminosity or color  
<img width="572" alt="Before classification and after image classification" src="https://github.com/user-attachments/assets/687bb021-83e4-4635-8aa3-969b4533ca30">

<br>

Image classification through the quantitative analysis of RGB values, utilizing metrics such as contrast (standard deviation of pixel intensities), luminosity (average brightness), and color attributes (hue, saturation, and lightness) for categorization, without relying on AI or machine learning techniques. This process involves processing a directory of images, analyzing their visual attributes, and then copying and organizing them into subdirectories based on these attributes.

- Standard Deviation (for contrast) - Measured by the standard deviation of pixel values.
- Luminosity (Based on the most dominant color 0 - 255)
- HSL (mainly for hue)  


## Benefits:

Ability to categorise images based on e.g. singular luminosity value, color (e..g: show only red images), hue, luminosity intensity. If image has certain contrast to luma to color ratio it could be possible to say how likely it is a picture of a dress or a tshirt. 


### Some of the use-case examples:

1. *Find all pink images*: Look in the hue/320-359/ directory for light pink and hue/0-39/ for darker pinks.
2. *Identify black and white images*: Check the std/0-39/ directory for images with low standard deviation.
3. *Separate dark and light images*: Use the Luminosity folders to distinguish between dark (0-74) and light (175-249) images.
4. *Find high-contrast images*: Look in the higher std/ folders (e.g., 120-159) for images with high contrast.
5. *Group images by color temperature*: Warm colors will be in hue/0-39/ and hue/320-359/, cool colors in hue/180-239/.
6. *Identify monochromatic images*: Look for images that appear in low std/ folders and have consistent hue categorization.
7. *Separate vivid and muted images*: Vivid images will likely have higher std values, while muted images will have lower std values.
8. *Identify images with similar color palettes*: Group images that appear in the same hue/ and std/ categories.
9. *Find "golden hour" photos:* Look for images in the hue/40-79/ (orange/golden) category with medium to high luminosity.


3 scripts are provided: 
- `image_classification_by_STD_Luminosity_HUE.py` - classify image based on 3 parameters std, luminosity, hue.
- `image_classification_by_STD_SKU.py` - classify image based on std (optimised for keeping images with the same SKU together)
- `image_classification_by_STD.py` - classify image based on std


## Usage  
1. Open the script and modify the following parameters in the `main()` function:
	- `input_folder`: Path to the directory containing your images
	- `output_folder`: Path where categorized images will be saved
	- `recursive`: Set to `True` for recursive directory scanning, `False` otherwise
	- `DELETE_ORIGINALS` : Set to `True` to  move files or `False` to copy instead;
	- `LUMINOSITY_INTERVAL`, `HUE_INTERVAL` , `STD_INTERVAL`: Adjust these to change the granularity of categorization
2. Run the script  


### Sample Output Example:
Let's assume we set the following parameters:

```sample_parameters
LUMINOSITY_INTERVAL = 25
STD_INTERVAL = 40
HUE_INTERVAL = 40

input_folder contains 1000 images
```

The script will create a directory structure in the specified output folder:

```sample_directory_structure
test-data/
├── Luminosity/
│   ├── 0-24/
│   ├── 25-49/
...
├── std/
│   ├── 0-39/
│   ├── 40-79/
│   ├── 80-119/
│   └── 120-159/
└── hue/
    ├── 0-39/
    ├── 40-79/
...
```

Each subdirectory would contain copies of the images that fall into that category.
