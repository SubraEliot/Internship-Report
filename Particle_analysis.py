
import cv2 as cv
import numpy as np
import pylab
import matplotlib.pyplot as plt
import os
from PIL import Image
from skimage import io, measure
import csv

""" The goal of this script is to perform a particles analysis on a 12-bit image.
with the k means color segmentation, otsu thresholding, contour detection and area filtering.


At the end, this test isn t very usefully because the noise and the particles are too close in intensity. Mainly because we had a gain
of times 8 we we recorded the images. So the noise is amplified too much."""


""" Filtre laplacien"""
def kmeans_color_quantization(image, clusters=2, rounds=1):
    h, w = image.shape[:2]
    samples = np.zeros((h * w, 1), dtype=np.float32)
    count = 0

    for x in range(h):
        for y in range(w):
            samples[count] = image[x][y]
            count += 1

    compactness, labels, centers = cv.kmeans(samples,
            clusters, 
            None,
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10000, 0.0001), 
            rounds, 
            cv.KMEANS_RANDOM_CENTERS)
    
    centers = np.uint16(centers)
    
    res = centers[labels.flatten()]
    res = res.reshape((image.shape))
    if GLOBAL_display:
        print("center 1", centers[:, 0])
        print("kmeans shape", res.shape)
    return res, samples.reshape((image.shape))

def sobel_operator(image):
    """
    Apply a Sobel operator to the image.
    """
    sobel_x = np.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]])
    sobel_y = np.array([[1, 2, 1],
                         [0, 0, 0],
                         [-1, -2, -1]])
    filtered_image_x = cv.filter2D(image, -1, sobel_x)
    filtered_image_y = cv.filter2D(image, -1, sobel_y)
    filtered_image = np.sqrt(filtered_image_x**2 + filtered_image_y**2)
    #filtered_image = np.round(filtered_image)
    #filtered_image = np.clip(filtered_image, 0, 4095)  # Clip values to 12-bit range
    return filtered_image

def filtre_high_pass(image, filtre):
    """
    Apply a high-pass filter to the image.
    """
    filtered_image = cv.filter2D(image, -1, filtre)
    return filtered_image

def plot_image(img, title="Image"):
    """
    Plot an image from a given path.
    """
    #img = Image.open(Path)
    img = np.array(img, dtype=np.uint16)
    plt.figure()
    plt.imshow(img, cmap='gray')  # Assuming 12-bit image
    plt.colorbar()
    plt.title(title)
    #plt.show()

def plot_histogram(Path):
    """
    Plot the histogram of an image from a given path.
    """
    # Ouvre le fichier TIF
    img = Image.open(Path)
    pixels = np.array(img)
    plt.figure()
    plt.hist(pixels.flatten(), bins=round(4095), color='black', log=False)
    plt.title(f"Histogramme 12 bits of {Path}")
    plt.xlabel("Niveau de gris")
    plt.ylabel("Nombre de pixels")
    #plt.show()

def compute_particle_analysis(image, MAX_AREA_THRESHOLD=9, MIN_AREA_THRESHOLD=1):
    # Perform kmeans color segmentation, grayscale, Otsu's threshold
    kmeans, original_reshaped = kmeans_color_quantization(image, clusters=2)
    #plot_image(kmeans, title='KMeans Segmentation')
    #plt.show()
    thresh = cv.threshold(kmeans, 0, 4095, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    if GLOBAL_display:
        plot_image(thresh, title='Otsu Thresholding')
        print(thresh[np.where(thresh > 0)])
    # Find contours, remove tiny specs using contour area filtering, gather points
    particles = []


    # Trouver les contours
    cnts = measure.find_contours(thresh, fully_connected="high")
    if GLOBAL_display:
        print("Number of contours found:", len(cnts))
        plot_contours(img, cnts)

    for c in cnts:
        c = np.array(c, dtype=np.int32) # Conversion en int32 pour etre utilisable dans cv2.drawContours
        area = cv.contourArea(c)
        if area > MAX_AREA_THRESHOLD or area < MIN_AREA_THRESHOLD: # Supprime les particules trop grandes
            cv.drawContours(thresh, [c], -1, 0, -1)
        else:
            (x, y), radius = cv.minEnclosingCircle(c)
            particles.append([int(x), int(y), round(radius, 2), round(area, 2)])
    
    if GLOBAL_display:
        plot_image(thresh, title='KMeans Segmentation')
        plt.show()
    return np.array(particles)

def particle_analysis(image, path_save=None,MAX_AREA_THRESHOLD=15, MIN_AREA_THRESHOLD=1, path_mask=None):
    # Put mask if provided
    if path_mask is not None:
        mask = Image.open(path_mask)
        mask = np.array(mask, dtype=np.uint16)
        image = np.where(mask > 0, image, 0)

    if GLOBAL_display:
        plot_image(image, "Image with mask applied")
        print("image shape", image.shape)
        plt.show()

    particles = compute_particle_analysis(image, MAX_AREA_THRESHOLD, MIN_AREA_THRESHOLD)
    n_particles = len(particles)
    avg_size = np.mean(particles[:, 2])
    avg_area = np.mean(particles[:, 3])

    if GLOBAL_display:
        print(f"Number of particles found: {n_particles}")
        print(f"Average particle size: {avg_size}")
        print(f"Average particle area: {avg_area}")

    if path_save is not None:
        header_lines = f"### \n"
        header_lines += f"### Picture : {name} \n"
        header_lines += f"### Parameters of the particles analysis \n"
        header_lines += f"### \n"
        header_lines += f"Max area threshold : {MAX_AREA_THRESHOLD}\n"
        header_lines += f"Min area threshold : {MIN_AREA_THRESHOLD}\n"
        header_lines += f"Mask applied : {path_mask}\n"
        header_lines += f"Number of particles found : {len(particles)}\n"
        header_lines += f"Average particle size : {avg_size}\n"
        header_lines += f"Average particle area : {avg_area}\n"
        header_lines += "### \n"
        header_lines += "### Data \n"
        header_lines += "### \n"
        header_lines += "X,Y,Radius,Area\n"
        np.savetxt("particle_analysis.csv", particles, delimiter=",", fmt="%s", header=header_lines)
    return n_particles, avg_size, avg_area

def plot_contours(image, contours, title="Particles found"):
    """
    Plot an image with its contours overlaid.
    
    Parameters:
        image (ndarray): The original image.
        contours (list of ndarray): List of (K, 2) ndarrays representing contours.
        title (str): Title of the plot.
    """
    plt.figure()
    plt.imshow(image, cmap='gray')  # Affiche l'image en niveaux de gris
    plt.title(title)
    
    # Parcourir et tracer chaque contour
    count = 0
    for contour in contours:
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2, label="Contour")  # Inverser row/column pour correspondre à x/y
        count += 1

    plt.legend(["Contours"])
    plt.colorbar()
    plt.show()

filtre_high = np.array([[-1, -1, -1],
                        [-1, 16, -1],
                        [-1, -1, -1]])

filtre_low = np.array([[1, 1, 1],
                       [1, 1, 1],
                       [1, 1, 1]]) / 9

GLOBAL_display = True
#Path = os.path.join("modify_pic", "mod_1.tif")
#Path = os.path.join("test_tif_format", "original_pic", "25400ns000000001.tif")
Path = os.path.join("test_tif_format", "test_image.tif")

img = Image.open(Path)

plot_image(img, "original image")
plot_histogram(Path)
pixels = np.array(img, dtype=np.float64) # Use float64 for precision in filtering
#pixels = pixels[0:1200, :]
print(len(pixels)* len(pixels[0]))
img_high_filtered = sobel_operator(pixels)
#plot_image(img_high_filtered, "Gradient Image")
#img_high_filtered = filtre_high_pass(pixels, filtre_high)
plot_image(img_high_filtered, "Gradient + filtre Image")
name = "filtered_mod_1.tif"
# Convert back to uint16 for saving
# # Plot the filtered image
# plt.figure()
# plt.imshow(img_high_filtered, cmap='gray')  # Assuming 12-bit image
# plt.colorbar()
# plt.title("Filtered Image")
# # Make histogram of the filtered image
# plt.figure()
# plt.hist(img_high_filtered.flatten(), bins=round(4095), color='black', log=True)
# plt.title(f"Histogramme filtre passe haut")
# plt.xlabel("Niveau de gris")
# plt.ylabel("Nombre de pixels")
# plt.show()
n_pix = len(pixels)* len(pixels[0])
n_particles, avg_size, avg_area = particle_analysis(img_high_filtered, path_save="particle_analysis.csv")

avg_n_part_IW = n_particles / n_pix* (32*32)
print(f"Average number of particles per IW: {avg_n_part_IW}")
plt.show()