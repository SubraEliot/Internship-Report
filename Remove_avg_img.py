from PIL import Image
import matplotlib.pyplot as plt
import os
import numpy as np
import re

def plot_image(Path, title="Image"):
    """
    Plot an image from a given path.
    """
    img = Image.open(Path)
    pixels = np.array(img, dtype=np.uint16)
    plt.figure()
    plt.imshow(img, cmap='gray')  # Assuming 12-bit image
    plt.title(title)
    plt.colorbar()
    #plt.show()

def get_image_info(img):
    print(f"image display name : {img.filename}")  # Affiche le nom du fichier
    print(f"image size : {img.size} ")  # Affiche la taille de l'image
    print(f"image mode : {img.mode} ")
    pixels = np.array(img)
    print(f"min intensity {pixels.min()}, max intensity {pixels.max()}")  # Doit donner 0 et 4095 si 12 bits

def plot_histogram(Path):
    """
    Plot the histogram of an image from a given path.
    """
    # Ouvre le fichier TIF
    img = Image.open(Path)
    pixels = np.array(img)
    plt.figure()
    plt.hist(pixels.flatten(), bins=round(4095), range=(0, 4095), color='black', log=True)
    plt.title(f"Histogramme 12 bits of {Path}")
    plt.xlabel("Niveau de gris")
    plt.ylabel("Nombre de pixels")
    #plt.show()

def compute_image_average(folder_path):
    tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.tif') and os.path.isfile(os.path.join(folder_path, f))]
    if not tif_files:
        print("No TIF files found in the specified folder.")
        return

    # Open the first image to get dimensions
    img = Image.open(tif_files[0])
    sum_even = np.zeros_like(np.array(img), dtype=np.float64)
    sum_odd = np.zeros_like(np.array(img), dtype=np.float64)
    count_even = 0
    count_odd = 0

    for count, file in enumerate(tif_files, start=1):
        img = Image.open(file)
        pixels = np.array(img, dtype=np.float64)
        if count % 2 == 0:
            sum_even += pixels
            count_even += 1
        else:
            sum_odd += pixels
            count_odd += 1

        if count % 20 == 0:
            print(f"Processed {count} images")

    # Calculate averages
    if count_even > 0:
        sum_even = np.clip(sum_even / count_even, 0, 4095)
        sum_even = np.round(sum_even).astype(np.uint16)
        img_avg_e = Image.fromarray(sum_even)
        img_avg_e.save("average_even.tif")

    if count_odd > 0:
        sum_odd = np.clip(sum_odd / count_odd, 0, 4095)
        sum_odd = np.round(sum_odd).astype(np.uint16)
        img_avg_o = Image.fromarray(sum_odd)
        img_avg_o.save("average_odd.tif")

def sup_avg_image(im1, im_avg):
    im1 = np.array(im1, dtype=np.float64)
    im_avg = np.array(im_avg, dtype=np.float64)
    mod_img = np.clip(im1 - im_avg, 0, 4095)
    mod_img = np.round(mod_img).astype(np.uint16)  # Round the values
    return mod_img

def save_image(image, path):
    """
    Save an image to a specified path.
    """
    print("min:", image.min(), "max:", image.max())  # Ajoute ce contrôle
    img = Image.fromarray(image)
    img.save(path)

def sub_avg_image_batch(average_path_even, average_path_odd, folder_path="original_pic"):
    """
    Subtract the average image from all images in a folder.
    """
    os.makedirs("modify_pic", exist_ok=True)
    average_img_even = Image.open(average_path_even)
    average_img_odd = Image.open(average_path_odd)

    tif_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.tif') and os.path.isfile(os.path.join(folder_path, f))]
    count = 1
    print(f"Found {len(tif_files)} tif files in {folder_path}")
    for file in tif_files:
        img = Image.open(os.path.join(file))
        if count % 2 == 0:
            modified_img = sup_avg_image(img, average_img_even)
        else:
            modified_img = sup_avg_image(img, average_img_odd)
        if count % 20 == 0:
            print(f"Modify avg {count} images")
        # Save the modified image in the new folder
        save_image(modified_img, os.path.join("modify_pic", f"mod_{count}.tif"))
        count += 1
        

""" MAIN CODE """
# folder_path = os.path.join("test_tif_format", "original_pic")
# first_pic = "25400ns000000001.tif"
# Path = os.path.join(folder_path, first_pic)
# # plot image
# #plot_image(Path)
# #get image info
# #img = Image.open(Path)
# #get_image_info(img)
# #plot histogram
# #plot_histogram(Path)
# #compute average images
# #compute_image_average(folder_path)
plot_image("test_tif_format/original_pic/25400ns000000001.tif", "Original 1 Image")
plt.show()
# plot_image("average_even.tif", "Average Even Image")
# #plot_image("average_odd.tif")
# # subtract average image from all images in the folder
# folder_modified = "modify_pic"
# path_average_even = "average_even.tif"
# path_average_odd = "average_odd.tif"
# #sub_avg_image_batch(path_average_even, path_average_odd, "test_tif_format\original_pic")
# #print(sup_avg_image(Image.open("test_tif_format/original_pic/25400ns000000001.tif"), Image.open("test_tif_format/average_even.tif")))
# plot_image("modify_pic/mod_1.tif", "Modified Image 1")
# plot_histogram(Path)
# plot_histogram("modify_pic/mod_1.tif")

#plot_histogram("modify_pic/mod_1.tif")


""" Test particle analysis """

# path = os.path.join("test_tif_format", "test_image.tif")
# plot_image(path, "Test Image")
# plot_histogram(path)

# folder_path = os.path.join("test_tif_format", "original_pic")
# first_pic = "25400ns000000001.tif"
# Path = os.path.join(folder_path, first_pic)
# plot_image(Path, "Original Image")
# plot_histogram(Path)

# Path = os.path.join("modify_pic", "mod_1.tif")
# plot_image(Path, "Modified Image")
# plot_histogram(Path)
# plt.show()

