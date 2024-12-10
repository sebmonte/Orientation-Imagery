#Script to resize images

import os
from PIL import Image

def resize_images(folder_path, new_size, new_prefix='resized_'):
    # Ensure the output directory exists
    output_folder = os.path.join(folder_path, 'resized')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file name starts with 'frame_' and ends with '.png'
        if filename.startswith('frame_') and filename.endswith('.png'):
            # Open the image file
            img_path = os.path.join(folder_path, filename)
            with Image.open(img_path) as img:
                # Resize the image
                img_resized = img.resize(new_size, Image.ANTIALIAS)
                
                # Create a new file name
                new_filename = filename
                
                # Save the resized image to the output folder
                new_img_path = os.path.join(output_folder, new_filename)
                img_resized.save(new_img_path)

    print(f"Resized images are saved in {output_folder}")

# My local path
folder_path = '/Users/montesinossl/Desktop/BlenderExp/Stimuli/'  
new_size = (514, 384)  # Specify the new size (width, height) in pixels

resize_images(folder_path, new_size)
