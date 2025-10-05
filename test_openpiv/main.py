"""Essaie de la librairie OpenPIV"""
import eliot_module
from openpiv import tools, pyprocess, validation, filters, scaling, lib, preprocess
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import imageio
import importlib_resources
import pathlib


eliot_module.batch_transform_tif_16_2_tif_8()

path_frame_a = "25400ns000000002_8bit.tif"
path_frame_b = "25400ns000000003_8bit.tif"

frame_a = tools.imread(path_frame_a)
frame_b = tools.imread(path_frame_b)
plt.imshow(frame_a)
plt.show()
""" PIV parameters """
window_size = 32
overlap = 16
search_area_size = 256
dt = 25*10**-6
""" Pre-processing"""
#reflexion = tools.find_reflexions([path_frame_a, path_frame_b], "reflexion.bmp")
reflexion = tools.imread("reflexion.bmp")
frame_a = frame_a - reflexion
frame_b = frame_b - reflexion
plt.imshow(frame_a)
plt.title("Frame A sans reflexion")
plt.show()

print(frame_a)
print(frame_a.shape)
x, y = pyprocess.get_coordinates(frame_a.shape, window_size, overlap)
print("voici x \n", x)
print("voici y \n", y)

polygone_mask = [[1766, 254], [1520, 161], [1520, 1872], [1424, 1872], [1294, 2012], [1294, 2325], [1515, 2325], [1515, 2350], [1766, 2350]]

xv, yv = np.meshgrid(np.arange(frame_a.shape[1]), np.arange(frame_a.shape[0]))
mask_boat = preprocess.prepare_mask_from_polygon(xv, yv, polygone_mask)
"""Inversion du masque"""
mask_boat = np.invert(mask_boat.astype(bool))
plt.imshow(mask_boat)
plt.title("masque")
plt.show()
frame_a = eliot_module.apply_mask_to_image(frame_a, mask_boat)
frame_b = eliot_module.apply_mask_to_image(frame_b, mask_boat)

imageio.imwrite("frame_a_masked_8bit.tif", frame_a)
imageio.imwrite("frame_b_masked_8bit.tif", frame_b)

plt.imshow(frame_a)
plt.title("Frame A avec masque")
plt.show()
preprocess.prepare_mask_on_grid(x, y, mask_boat)

""" PIV """

u, v, sig2noise = pyprocess.extended_search_area_piv(
    frame_a, frame_b, window_size=window_size, overlap=overlap, dt=dt,
)
scaling_factor = 2352/89
x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor)

tools.display_vector_field_from_arrays(x, y, u, v, flags=None, mask=None, scaling_factor=scaling_factor)

plt.imshow(sig2noise)
plt.colorbar()
plt.show()

""" Conclusion PIV a chier mais fonctionnelle !"""
