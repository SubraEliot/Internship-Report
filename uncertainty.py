""" 
The purpose of this script is to analyze uncertainty fields from PIV (Particle Image Velocimetry) analysis
results contained in .dat files. It visualizes the flag and uncertainty fields and computes RMS uncertainty
statistics across all available data files.

Author: [SUBRA Eliot]
Date: [02/09/2025]
"""

import matplotlib.pyplot as plt  # For plotting and visualization
import numpy as np               # For numerical operations and array handling
import os                        # For file system operations

# Configuration: specify which image to analyze in detail
n_img = "936"
first_img_path = "result/result000000"+ n_img +".dat"

# =============================================================================
# PART 1: READ AND PROCESS SINGLE IMAGE DATA FOR DETAILED VISUALIZATION
# =============================================================================

# Read the specified .dat file to analyze one image in detail
with open(first_img_path, "r") as file:
    lines = file.readlines()
    # Split each line into individual values (space-separated)
    data = [ligne.strip().split() for ligne in lines]

# Remove header (first 5 lines) and footer (last 34 lines) that contain metadata
data = data[5:-34]  
# Convert all string values to float for numerical processing
data = [[float(val) for val in ligne] for ligne in data]

# Extract relevant columns from the PIV data
uncertainty = np.array([row[14] for row in data])  # Column 15: uncertainty values (PIV measurement error)
flag = np.array([row[13] for row in data])         # Column 14: flag values (quality indicators)
uncertainty_sum = np.zeros_like(uncertainty)       # Initialize sum of uncertainties for averaging
previous_uncertainty_sum = np.zeros_like(uncertainty)  # For convergence criterion

# Create a copy of uncertainty for visualization purposes
sort_uncertainty = uncertainty.copy()
# Set uncertainty to -1 where flag=2 (invalid/poor quality measurements)
# This helps visualize problematic areas in the flow field
sort_uncertainty[flag==2] = -1

# Extract spatial coordinates (grid positions)
# Note: Conversion factor (89/2352) is commented out - would convert pixels to mm
X = np.array([row[0] for row in data])  # X coordinates 
Y = np.array([row[1] for row in data])  # Y coordinates 

# =============================================================================
# PART 2: VISUALIZATION OF FLAG AND UNCERTAINTY FIELDS
# =============================================================================

# Create side-by-side plots for flag and uncertainty fields
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left plot: Flag field visualization
# Flags indicate measurement quality: 0=good, 1=interpolated, 2=invalid, etc.
sc1 = ax1.scatter(X, Y, c=flag, cmap='viridis')
plt.colorbar(sc1, ax=ax1, label="Flag first image")
ax1.set_xlabel("X (mm)")
ax1.set_ylabel("Y (mm)")
ax1.set_title("Flag Field - Measurement Quality Indicators")

# Right plot: Uncertainty field visualization
# Shows spatial distribution of measurement uncertainties
# Invalid measurements (flag=2) are shown as -1 for easy identification
sc2 = ax2.scatter(X, Y, c=sort_uncertainty, cmap='viridis')
plt.colorbar(sc2, ax=ax2, label="Uncertainty first image")
ax2.set_xlabel("X (mm)")
ax2.set_ylabel("Y (mm)")
ax2.set_title("Uncertainty Field - Measurement Error Distribution")

# Optimize layout to prevent overlapping elements
plt.tight_layout()

# Save the figure as high-resolution PNG
plt.savefig("flag_uncertainty_"+n_img+".png", dpi=300)
plt.show()

# =============================================================================
# PART 3: COMPUTE RMS UNCERTAINTY FOR THE SELECTED IMAGE
# =============================================================================

# Filter out invalid measurements (flag=0 typically means no measurement)
uncertainty_without_flag_0 = uncertainty[flag!=0]

# Compute Root Mean Square (RMS) uncertainty
# RMS = sqrt(mean(uncertainties²)) - gives overall uncertainty magnitude
rms_uncertainty = 1/(len(uncertainty_without_flag_0))*(np.sum(uncertainty_without_flag_0**2))**0.5
print("RMS uncertainty for image "+n_img+" : ", rms_uncertainty)

# =============================================================================
# PART 4: BATCH ANALYSIS OF ALL DAT FILES - RMS UNCERTAINTY EVOLUTION
# =============================================================================

# Initialize arrays to store results from all files
directory = "result"          # Directory containing all .dat files
rms_array = []               # Array to store RMS uncertainty values
file_array = []              # Array to store file numbers for plotting
n_file = 0                   # Counter for processed files

# Process each .dat file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".dat"):  # Process only .dat files
        file_path = os.path.join(directory, filename)
        
        # Read and parse the current file (same process as above)
        with open(file_path, "r") as file:
            lines = file.readlines()
            data = [ligne.strip().split() for ligne in lines]

        # Remove header and footer, convert to float
        data = data[5:-34]  
        data = [[float(val) for val in ligne] for ligne in data]

        # Extract uncertainty and flag data
        uncertainty = np.array([row[14] for row in data])  # Uncertainty values
        flag = np.array([row[13] for row in data])         # Quality flags
        
        # Keep only valid measurements (exclude flag=0)
        uncertainty = uncertainty[flag!=0] 
        
        # Compute RMS uncertainty for this file
        rms_uncertainty = 1/(len(uncertainty))*(np.sum(uncertainty**2))**0.5
        
        # Store results for plotting
        rms_array.append(rms_uncertainty)
        n_file += 1
        file_array.append(n_file)
        
        # Print progress
        print("RMS uncertainty for image "+file_path+" : ", rms_uncertainty)

# =============================================================================
# PART 5: PLOT RMS UNCERTAINTY EVOLUTION ACROSS ALL IMAGES
# =============================================================================        

# Create time series plot of RMS uncertainty
plt.figure(figsize=(10, 6))
plt.plot(file_array, rms_array, marker='o', linewidth=2, markersize=4)
plt.xlabel("Image number")
plt.ylabel("RMS Uncertainty")
plt.title("RMS Uncertainty Evolution Across PIV Image Sequence")
plt.grid(True, alpha=0.3)  # Add grid for better readability
plt.tight_layout()
plt.show()