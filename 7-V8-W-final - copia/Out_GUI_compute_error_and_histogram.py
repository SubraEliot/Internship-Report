import matplotlib as plt
import numpy as np
from post_analysis import *
import scipy.integrate as sc

"""
This script is used to analyze the experimental data and produce an histogram of the velocity error
between t_start and t_end."""

# Experiment folder
folder_exp = "experiments\exp_2025-07-02_14-24-48"

# Time window for analysis
t_start = 200
t_end = 1000

# Load data
t, v, v_target, T, Pressure_pitot, P_amb, Control_signal, dic_para = load_data(folder_exp + "\\row_data")

# Convert to numpy arrays
v = np.array(v)
v_target = np.array(v_target)
t = np.array(t)

# Find indices for t_start and t_end
indice_t_start = np.argwhere(t > t_start)[0][0]
indice_t_end = np.argwhere(t > t_end)[0][0]

# Slice the data between t_start and t_end
v = v[indice_t_start:indice_t_end]
v_target = v_target[indice_t_start:indice_t_end]
t = t[indice_t_start:indice_t_end]

dt = t[-1] - t[0]

# Compute mean velocity
v_mean = np.mean(v)

# Compute the integral of the absolute error
int_v_diff = sc.simpson(np.abs(v-v_target), t)/dt
print("mean velocity ", v_mean, "error" , int_v_diff*100, "%")

# Histogram
counts, bins, patches = plt.hist(np.abs(v-v_target), bins=20)

for count, bin_left, bin_right in zip(counts, bins[:-1], bins[1:]):
    plt.text((bin_left + bin_right) / 2, count, int(count),
             ha='center', va='bottom', fontsize=8)
plt.xlabel('|v-v_target|')
plt.ylabel('Fréquency')
plt.title('Histogram of v')
plt.show()