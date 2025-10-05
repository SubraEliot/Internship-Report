import pickle
import matplotlib.pyplot as plt

""" If you want to see with matplotlib plot old experiments, you can use this script."""

# Path parameters 
folder = "experiments/"
filename = folder + "data_2025-07-01_14-35-41_post_pros_fft_0.pkl"

# Load previous matplotlib graph
with open(filename, 'rb') as f:
    fig = pickle.load(f)
plt.figure(fig.number)
plt.show()

