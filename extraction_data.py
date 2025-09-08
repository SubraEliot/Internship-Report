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
    """ Extract data from a .dat file and return X, Y coordinates and values from the specified column.
    path : path to the .dat file
    col : column index to extract (0-based)
    name_col : name of the column to display
    pix_2_mm_fact : factor to convert pixels to mm (default is 89/2352)
    header : number of header lines to skip (default is 5)
    footer : number of footer lines to skip (default is 34)
    is_display : if True, display the field using a scatter plot
    Returns 
    X : 2D array of X coordinates
    Y : 2D array of Y coordinates
    Val : 2D array of values
    """
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
    # Transform Val into a 2D array based on unique X and Y values
    len_X = len(np.unique(X))
    len_Y = len(X) // len_X

    X = X.reshape((len_Y, len_X))
    Y = Y.reshape((len_Y, len_X))
    Val = np.array(Val).reshape((len_Y, len_X))
    return X, Y, Val 

def plot_field_X_Y_Val(X, Y, Val, name_col, path_save=None):
    """ Plot a field given X, Y coordinates and corresponding values Val. 
    X : 2D array of X coordinates
    Y : 2D array of Y coordinates
    Val : 2D array of values to plot
    name_col : name of the field to display
    path_save : if not None, save the figure to this path
    """
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(X, Y, c=Val, cmap='viridis')
    plt.colorbar(sc, label=f" {name_col}")
    plt.xlabel("X (mm)")
    if path_save is not None:
        plt.savefig(f"{path_save}-{name_col}-fig.png", dpi=300)
    plt.ylabel("Y (mm)")
    plt.show()


# Example usage:
"""
first_img_path = "PIV-04-07-25_img_1.dat"
X, Y, Speed = extraction_data(first_img_path, 13, "Speed first image", is_display=False)
plot_field_X_Y_Val(X, Y, Speed, "Speed first image", path_save="PIV-04-07-25_img_1-Speed")
"""
