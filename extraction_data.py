import matplotlib.pyplot as plt
import numpy as np
import os

""" #######
This file contains functions for extracting and plot data from PIV .dat files.
col 0 :"X (mm)"
col 1 :"Y (mm)"
col 2 :"Z (mm)"
col 3 :"U (m/s)"
col 4 :"V (m/s)"
col 5 :"W (m/s)"
col 6 :"Speed (m/s)"
col 7 :"Vorticity"
col 8 :"U-std"
col 9 :"V-std"
col 10 :"W-std"
col 11 :"Speed-std"
col 12 :"Vorticity-std"
col 13 :"Flag"
col 14 :"Uncertainty"
#######"""

def extraction_data(path, col, name_col, pix_2_mm_fact = 89 / 2352,header=5, footer=34, is_display=False):
    with open(path, "r") as file:
        lines = file.readlines()
        data = [ligne.strip().split() for ligne in lines]

    data = data[header:-footer]  # Remove unnecessary header and footer lines
    data = [[float(val) for val in ligne] for ligne in data]

    Val = [row[col] for row in data]  # Extract speed values from the specified column

    # Convert grid coordinates from pixels to mm
    X = np.array([row[0] for row in data]) * pix_2_mm_fact
    Y = np.array([row[1] for row in data]) * pix_2_mm_fact

    # Plot the speed field for the first image
    if is_display:
        plt.figure(figsize=(8, 6))
        sc = plt.scatter(X, Y, c=Val, cmap='viridis')
        plt.colorbar(sc, label=f" {name_col}")
        plt.xlabel("X (mm)")
        plt.savefig(f"{path}-{name_col}-fig.png", dpi=300)
        plt.ylabel("Y (mm)")
        plt.show()
    return X, Y, Val 

first_img_path = "try_2000000002.dat"
extraction_data(first_img_path, 13, "Flag first image", is_display=True)
