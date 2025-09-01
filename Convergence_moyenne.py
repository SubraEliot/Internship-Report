import matplotlib.pyplot as plt
import numpy as np
import os

""" #######
The purpose of this script is to calculate the average velocity from the results of the PIV analysis
contained in .dat files
#######"""

first_img_path = "25400ns_HD_BMP_Data/25400ns000000001.dat"

# Read the first .dat file to initialize variables and get grid coordinates
with open(first_img_path, "r") as file:
    lines = file.readlines()
    data = [ligne.strip().split() for ligne in lines]

data = data[5:-34]  # Remove unnecessary header and footer lines
data = [[float(val) for val in ligne] for ligne in data]

sp = [row[6] for row in data] # Extract speed values from the 7th column

speed_sum = np.zeros_like(sp) # Initialize sum of speeds for averaging
previous_speed_sum = np.zeros_like(sp) # For convergence criterion

# Convert grid coordinates from pixels to mm
X = np.array([row[0] for row in data]) * (89 / 2352)  
Y = np.array([row[1] for row in data]) * (89 / 2352) 

# Plot the speed field for the first image
plt.figure(figsize=(8, 6))
sc = plt.scatter(X, Y, c=sp, cmap='viridis')
plt.colorbar(sc, label=f" Speed first image (m/s)")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.show()

criterion_conv = []  # List to store convergence criterion values
n_file = 1           # Counter for the number of processed files
n_points = len(X)    # Number of grid points

# Loop through all .dat files in the directory
for file in os.listdir('25400ns_HD_BMP_Data'):

    if file.endswith('.dat'):
        path = file
    with open("25400ns_HD_BMP_Data/" + path, "r") as file:
        lines = file.readlines()
        data = [line.strip().split() for line in lines]

    data = data[5:-34]  # Remove unnecessary header and footer lines
    data = [[float(val) for val in line] for line in data]
    speed = np.array([row[6] for row in data])  # Extract speed values
    speed_sum += speed # Accumulate speed for averaging
    # Compute convergence criterion
    if n_file == 1:
        criterion_conv.append(np.sum(np.abs(speed) / n_points))
    else:
        criterion_conv.append(np.sum(np.abs(speed_sum/n_file - previous_speed_sum/(n_file-1)))/ n_points)
    
    # Plot and save the average speed field every 10 files
    if n_file % 10 == 0:
        print(f"Processing file {n_file}: {path} with convergence criterion {criterion_conv[-1]}")
        plt.figure(figsize=(8, 6))
        sc = plt.scatter(X, Y, c=speed_sum/(n_file), cmap='viridis')
        plt.colorbar(sc, label=f"Avg speed (m/s)")
        plt.xlabel("X (mm)")
        plt.ylabel("Y (mm)")
        plt.title("Speed field average over " + str(n_file + 1) + " pictures")
        plt.savefig("pictures/field_speed_" + str(n_file) + ".png")
        plt.close()

    n_file += 1
    previous_speed_sum = speed_sum.copy()   # Update previous sum for next iteration

# Compute and plot the final average speed field
speed_sum = speed_sum/(n_file)
sc = plt.scatter(X, Y, c=speed_sum, cmap='viridis')
plt.colorbar(sc, label=f"Avg speed (m/s)")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.title("Average speed field over " + str(n_file) + " pictures")
plt.legend()
plt.savefig("pictures/avg_speed_over_" + str(n_file) + "images.png")
plt.show()

# Plot the convergence criterion evolution
n_pict = np.arange(1, n_file)
plt.plot(n_pict, criterion_conv, marker='o')
plt.xlabel("Number of pictures")
plt.ylabel("Convergence criterion")
plt.title("Convergence criterion over pictures")
plt.show()

