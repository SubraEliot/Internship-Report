import numpy as np
from PIL import Image
from openpiv import tools
from typing import Any, Union, List, Optional
import os 
import imageio.v2 as imageio

def imread_tif_16_bit(file_path: str) -> np.ndarray:
    """Lit une image TIFF 16 bits et renvoie un tableau numpy."""
    img = Image.open(file_path)
    img_array = np.array(img)
    return img_array

def save_and_normalize_image(img_array: np.ndarray, output_path: str) -> None:
    """Sauvegarde et normalise une image."""
    # Normalize the image array to the range [0, 255]
    img_normalized = (img_array / np.max(img_array) * 255).astype(np.uint8)
    # Save the normalized image
    imageio.imwrite(output_path, img_normalized)

def transforme_tif_16_2_tif_8(file_path: str, output_path: str) -> None:
    """Transforme une image TIF 16 bits en TIF 8 bits."""
    img_array = imread_tif_16_bit(file_path)
    save_and_normalize_image(img_array, output_path)

def batch_transform_tif_16_2_tif_8(input_folder: str = os.getcwd(), output_folder: str = os.getcwd()) -> None:
    """Transforme plusieurs images TIF 16 bits en TIF 8 bits."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        condition = filename.endswith(".tif")  and not filename.endswith("_8bit.tif")
        if condition:
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_8bit.tif")
            transforme_tif_16_2_tif_8(input_path, output_path)
            print(f"Transformed {input_path} to {output_path}")


def apply_mask_to_image(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Applique un masque à une image."""
    return image * mask