import matplotlib.pyplot as plt
import numpy as np
import os
from extraction_data import extraction_data, plot_field_X_Y_Val

""" #######
Analyse Flag values from PIV .dat files.
Computation of Cr, Cr tilde, Cr local, histogram of N2, plot of Flag and N2 fields
#######"""

""" Plot Flag field for the first image """
first_img_path = "PIV-04-07-25_img_1.dat"
X, Y, Flag = extraction_data(first_img_path, 13, "Flag first image", is_display=False, pix_2_mm_fact=135/2352, header=5, footer=34)

""" Compute Cr tilde"""
flag_1 = np.size(np.where(Flag == 1)[0])
flag_2 = np.size(np.where(Flag == 2)[0])
flag_0 = np.size(np.where(Flag == 0)[0])
print(f"flag 0 : {flag_0}, flag 1 : {flag_1}, flag 2 : {flag_2} \n")
Cr_tilde = flag_2 / (flag_1 + flag_2)
print(f"Cr : {flag_2 / (flag_0 + flag_1 + flag_2)} \n")
print(f"Cr tilde: {Cr_tilde} \n")
print(f"ratio mask : {flag_0 / (flag_0 + flag_1 + flag_2)} \n")

""" Compute N2(pixel) : number of neighbors with Flag=2 for each pixel"""

X, Y, Flag = extraction_data(first_img_path, 13, "Flag first image", is_display=False, pix_2_mm_fact=135/2352, header=5, footer=34)

n_neighbors_flag_2 = np.zeros_like(Flag)
for i in range(len(Flag)):
    for j in range(len(Flag[0])):
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < len(Flag) and 0 <= nj < len(Flag[0]):
                    if Flag[ni][nj] == 2:
                        n_neighbors_flag_2[i][j] += 1
        #print(i, j, n_neighbors_flag_2[i][j])

plot_field_X_Y_Val(X, Y, n_neighbors_flag_2, "Number of neighbors with Flag=2", path_save="PIV-04-07-25_img_1-neighbors-Flag2")

plt.figure(figsize=(8, 6))
plt.subplot(1, 2, 1)
sc = plt.scatter(X, Y, c=Flag, cmap='viridis')
plt.colorbar(sc, label=f" Flag")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.subplot(1, 2, 2)
sc = plt.scatter(X, Y, c=n_neighbors_flag_2, cmap='viridis')
plt.colorbar(sc, label=f" Number of neighbors with Flag=2")
plt.xlabel("X (mm)")
plt.ylabel("Y (mm)")
plt.show()

""" Compute the average number of neighbors with Flag=2 over all pixels"""

avg_n_neighbors_flag_2 = np.mean(n_neighbors_flag_2)
print(f"Average number of neighbors with Flag=2: {avg_n_neighbors_flag_2}")

""" Compute the max N2"""

max_n_neighbors_flag_2 = np.max(n_neighbors_flag_2)
print(f"Max number of neighbors with Flag=2: {max_n_neighbors_flag_2}")

""" Compute N2 > 2"""
n_neighbors_flag_2_gt_2 = np.size(np.where(n_neighbors_flag_2[np.where(Flag != 0)] > 2)[0]) /(flag_1 + flag_2)
print(f"N2 > 2: {n_neighbors_flag_2_gt_2}")

""" Compute histogram of N2 values"""

plt.figure(figsize=(8, 6))
plt.hist(n_neighbors_flag_2[np.where(Flag != 0)].flatten(), bins=np.arange(-0.5, 9.5, 1), density=True, alpha=0.7, color='blue')
#plt.hist(n_neighbors_flag_2.flatten(), bins=np.arange(-0.5, 9.5, 1), density=True, alpha=0.7, color='blue')
plt.xlabel("Number of neighbors with Flag=2")
plt.ylabel("Probability")
plt.title("Histogram of number of neighbors with Flag=2 with ignoring Flag=0")
plt.grid()
plt.show()

