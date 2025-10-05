import pickle
import shared
import matplotlib.pyplot as plt
import csv
from scipy.fft import fft, fftfreq
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def load_data(filename):
    """ Load experimental data from a CSV file.
    This function reads a CSV file (skipping the first 30 lines where we have the metadata)
    and extracts the following columns: time, measured velocity, target velocity, temperature,
    pitot pressure, ambient pressure, and control signal. Each column is converted to a list of floats.
    Args:
        filename (str): Path to the CSV file (without the '.csv' extension).
    Returns:
        tuple: (t, v, v_target, T, Pressure_pitot, P_amb, Control_signal)
            t (list of float): Time values.
            v (list of float): Measured velocity values.
            v_target (list of float): Target velocity values.
            T (list of float): Temperature values.
            Pressure_pitot (list of float): Pitot pressure values.
            P_amb (list of float): Ambient pressure values.
            Control_signal (list of float): Control signal values.
            dic_para (dicionnary): parameters of the experiment, be carefull the values type of the variable stock in the dictionnary are str
    """
    filename += ".csv"
    # Extract the old dictionnary
    dic_para = {}
    with open(filename, "r", newline='') as file:
            reader = csv.reader(file)
            lines = list(reader)
            # Parse parameter dictionary from header (lines 4-30)
            for line in lines[4:32]:
                try :
                    if ':' in line[0]:
                        parts = line[0].split(":", 1)
                        key = parts[0].strip()
                        value = parts[1].strip()
                        dic_para[key] = value
                except:
                    pass
    with open(filename, "r", newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)[32:]  # Skip the first 30 lignes
        # Conversion en float pour chaque colonne
        t, v, v_target, T, Pressure_pitot, P_amb, Control_signal = [], [], [], [], [], [], []
        for row in lines:
            if len(row) < 7:
                continue  # Skip the not complet ligne
            # Creat list for t, v, v_target ....
            t.append(float(row[0]))
            v.append(float(row[1]))
            v_target.append(float(row[2]))
            T.append(float(row[3]))
            Pressure_pitot.append(float(row[4]))
            P_amb.append(float(row[5]))
            Control_signal.append(float(row[6]))
    return t, v, v_target, T, Pressure_pitot, P_amb, Control_signal, dic_para

def fft_signal(signal, sampling_rate):
    """Compute the Fast Fourier Transform (FFT) of a signal.
    This function calculates the FFT of the input signal and returns the frequency bins
    and the corresponding amplitude spectrum (normalized). Only the positive frequencies are returned.
    Args:
        signal (array-like): The input signal to analyze.
        sampling_rate (float): The sampling rate of the signal in Hz.
    Returns:
        tuple: (xf, yf)
            xf (numpy.ndarray): Array of frequency bins (Hz).
            yf (numpy.ndarray): Normalized amplitude spectrum.
    """
    N = len(signal)
    T = 1.0 / sampling_rate
    yf = fft(signal)
    xf = fftfreq(N, T)[:N//2]
    return xf, 2.0/N * np.abs(yf[:N//2]) # We take the abs to compute the amplitude of the fft, We multiply by 1/N to normalize the fourier transform, We multiply by 2 because we conserve only half of the signal and we don t want to forget si negative signal

def criterion_analysis(y, target):
    """    Identify intervals where the measured signal is close to the target value.
    This function compares the measured signal to the target value and finds indices
    where the absolute difference is less than 5% of the target. It then groups these indices
    into continuous intervals, which can be used for further analysis (e.g., FFT).
    Args:
        y (array-like): Measured signal values.
        target (array-like): Target signal values.
    Returns:
        tuple: (extrem, msg)
            extrem (list of int): List of interval boundaries (start and end indices).
            msg (str): Message describing the number of intervals found or if the target was not reached.
    """
    y = np.array(y)                             # Convert input to numpy array for vectorized operations
    target = np.array(target)                   # Convert target to numpy array
    diff = np.abs(y - target)                   # Compute absolute difference between measured and target
    indices = np.argwhere(diff < 0.05*target)   # Find indices where the difference is less than 0.05
    indices = indices.flatten()                 # Flatten the array to 1D
    # If not enough points are close to the target, return an error message
    if len(indices) < 2:
        msg = "Target velocity not reached \n"
        return [], msg
    extrem = [indices[0]]                       # Start with the first index as the beginning of the first interval
    # Loop through indices to find discontinuities (gaps > 1) and mark interval boundaries
    for i in range(len(indices)-1):
        if indices[i+1] - indices[i] > 1:
            extrem.append(indices[i])           # End of previous interval
            extrem.append(indices[i+1])         # Start of new interval
    extrem.append(indices[-1])                  # Add the last index as the end of the last interval
    msg = f"{len(extrem)} interval found for fft analysis \n" 
    return extrem, msg

def post_analysis(t , v, sampling_rate, target_velocity):
    """    Perform post-processing analysis on the velocity data.
    This function identifies intervals where the measured velocity is close to the target velocity,
    computes the FFT for each valid interval, and collects the results for further display.
    Args:
        t (array-like): Time values.
        v (array-like): Measured velocity values.
        sampling_rate (float): Sampling rate of the signal in Hz.
        target_velocity (array-like): Target velocity values.
    Returns:
        tuple: (freq_array, ffts_array, t_array, msg)
            freq_array (list): List of frequency arrays for each interval.
            ffts_array (list): List of FFT amplitude arrays for each interval.
            t_array (list): List of [start_time, end_time] for each interval.
            msg (str): Message summarizing the analysis results.
    """
    # Identify intervals where the measured velocity is close to the target
    extrem, msg = criterion_analysis(v,  target_velocity)

    ffts_array = []                                 # List to store FFT amplitude arrays for each interval
    freq_array = []                                 # List to store frequency arrays for each interval
    t_array = []                                    # List to store [start_time, end_time] for each interval
    # Loop through each interval (start/end pairs)
    for  i in range(0, len(extrem)-1, 2):
        start = extrem[i]
        end = extrem[i+1]
        # Only analyze intervals with enough data points
        if end - start > 10:
            # Subtract target to center the signal (removes DC component)
            segment = np.array(v[start:end]) - np.array(target_velocity[start:end])  # Normalize the segment to avoid fft pic in 0
            # Compute FFT for the segment
            xf, yf = fft_signal(segment, sampling_rate)
            ffts_array.append(yf)                   # Store FFT amplitude
            freq_array.append(xf)                   # Store frequency bins
            t_array.append([t[start], t[end]])      # Store interval time bounds
    # Update the message with the number of FFTs computed
    msg = msg + f"{len(ffts_array)} fft were computed\n"
    return freq_array, ffts_array, t_array, msg


def graph_interface_fft(t, v, sampling_rate, target_velocity):
    """    Display the FFT analysis results in a graphical Tkinter interface.
    This function performs post-processing analysis to identify intervals where the measured velocity
    is close to the target velocity, computes the FFT for each valid interval, and displays the results
    in a dedicated FFT viewer window. If no valid intervals are found, it returns a message.
    Args:
        t (array-like): Time values.
        v (array-like): Measured velocity values.
        sampling_rate (float): Sampling rate of the signal in Hz.
        target_velocity (array-like): Target velocity values.
        dic_para (dict) : Dictionnary of the old parameters 
    Returns:
        str: Message summarizing the FFT analysis results or indicating if no valid segments were found.
    """
    # Run the post-processing to get FFTs and intervals
    freq_array, ffts_array, t_array, msg = post_analysis(t, v, sampling_rate, target_velocity)
    # If no valid intervals were found, return a message
    if len(freq_array) == 0:
        msg += "No valid segments found for FFT analysis.\n"
        return msg
    else:
        # Create and display the FFT viewer window
        viewer = FFTViewer(freq_array, ffts_array, t_array, np.array(t), np.array(v))
        viewer.plot_fft()   # Plot the first FFT by default
        # Ensure proper closing of the viewer window
        viewer.protocol("WM_DELETE_WINDOW", viewer.on_closing_viewer)
        return msg


def plot_data(filename):
    """    Plot and save the main experimental data.
    This function loads the experimental data from a CSV file, creates a 2x2 grid of plots
    (velocity, temperature, pitot pressure, and control signal), and displays them using matplotlib.
    If data saving is enabled, it also saves the figure as a PNG image and as a pickle file
    (for later reloading with matplotlib).
    Args:
        filename (str): Path to the CSV file (without the '.csv' extension).
    Returns:
        None
    """
    # Load data from CSV file
    t, v, v_target, T, Pressure_pitot, P_amb, Control_signal, dic_para = load_data(filename+"\\row_data")
    v_target = np.array(v_target) # Convert to np array to use vector computation
    # Create a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, sharex=True, figsize=(10, 12))
    # Plot velocity and target velocity
    axs[0][0].plot(t, v, label='Velocity (m/s)', color="blue")
    axs[0][0].plot(t, v_target-float(dic_para["conv_factor"])*v_target, label='Low boundary conv (m/s)', linestyle='--', color="green")
    axs[0][0].plot(t, v_target+float(dic_para["conv_factor"])*v_target, label='Low boundary conv (m/s)', linestyle='--', color="red")
    axs[0][0].plot(t, v_target, label='Target velocity (m/s)', linestyle='--', color="orange")
    axs[0][0].set_xlabel('Time (s)')
    axs[0][0].set_ylabel('Velocity (m/s)')
    axs[0][0].set_title('Evolution of Velocity and Target Velocity')
    axs[0][0].legend()

    # Plot temperature
    axs[1][0].plot(t, T, label='Temperature (K)', color='tab:orange')
    axs[1][0].set_xlabel('Time (s)')
    axs[1][0].set_ylabel('Temperature (K)')
    axs[1][0].set_title('Evolution of Temperature')
    axs[1][0].legend()

    # Plot pitot pressure
    axs[1][1].plot(t, Pressure_pitot, label='Pitot Pressure (Pa)', color='tab:green')
    axs[1][1].set_xlabel('Time (s)')
    axs[1][1].set_ylabel('Pressure (Pa)')
    axs[1][1].set_title('Evolution of Pitot Pressure')
    axs[1][1].legend()

    # Plot control signal
    axs[0][1].plot(t, Control_signal, label='Control Signal (V)', color='tab:red')
    axs[0][1].set_xlabel('Time (s)')
    axs[0][1].set_ylabel('Control Signal (V)')
    axs[0][1].set_title('Evolution of Control Signal')
    axs[0][1].legend()
    # Adjust layout for better appearance
    plt.tight_layout()
    # If data saving is enabled, save the figure as pickle and PNG
    if shared.parameters["is_save_data"]:
        with open(filename + '\\plot.pkl', 'wb') as f:
            pickle.dump(fig, f)
        
        plt.savefig(filename + '\\plot.png', dpi=300, bbox_inches='tight')
    plt.show()
    

        

class FFTViewer(tk.Toplevel):
    """    A Tkinter window for interactive visualization of FFT analysis results.
    This class creates a window with two matplotlib subplots: one for the FFT amplitude spectrum
    and one for the corresponding time-domain velocity signal. Navigation buttons allow the user
    to browse through different FFT intervals. The window also supports saving the current figure
    if data saving is enabled.
    Args:
        freq_array (list): List of frequency arrays for each interval.
        ffts_array (list): List of FFT amplitude arrays for each interval.
        t_array (list): List of [start_time, end_time] for each interval.
        t_full (array-like): Full time array for the original signal.
        v_full (array-like): Full velocity array for the original signal.
    Methods:
        plot_fft(): Plot the FFT and corresponding time interval for the current index.
        prev_fft(): Show the previous FFT interval.
        next_fft(): Show the next FFT interval.
        on_closing_viewer(): Properly close the FFT viewer window.
    """
    def __init__(self, freq_array, ffts_array, t_array, t_full, v_full):
        super().__init__()
        self.title("FFT Viewer")
        self.freq_array = freq_array            # List of frequency arrays for each interval
        self.ffts_array = ffts_array            # List of FFT amplitude arrays for each interval
        self.t_array = t_array                  # List of [start_time, end_time] for each interval
        self.t_full = t_full                    # Full time array for the original signal
        self.v_full = v_full                    # Full velocity array for the original signal
        self.index = 0                          # Current interval index

        # Matplotlib Figure with 2 subplots: FFT (left), Time signal (right)
        self.fig, (self.ax_fft, self.ax_time) = plt.subplots(1, 2, figsize=(12, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self) # Insert the figure in the Tkinter window
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Navigation buttons for browsing FFT intervals
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.prev_btn = tk.Button(btn_frame, text="Précédent", command=self.prev_fft)
        self.prev_btn.pack(side=tk.LEFT, expand=True)
        self.next_btn = tk.Button(btn_frame, text="Suivant", command=self.next_fft)
        self.next_btn.pack(side=tk.RIGHT, expand=True)

    def plot_fft(self):
        # Clear previous plots
        # Create a new figure for saving (do not pickle the GUI figure)
        fig_save, (ax_fft_save, ax_time_save) = plt.subplots(1, 2, figsize=(12, 4))
        self.ax_fft.clear()
        self.ax_time.clear()
        # Plot FFT for the current interval
        self.ax_fft.plot(self.freq_array[self.index], self.ffts_array[self.index], marker="x")
        self.ax_fft.set_title(f"FFT n°{self.index+1}\n between {round(self.t_array[self.index][0], 1)} s and {round(self.t_array[self.index][1], 1)} s")
        self.ax_fft.set_xlabel("Frequency (Hz)")
        self.ax_fft.set_ylabel("Amplitude")
        # Plot time signal for the same interval
        t_start, t_end = self.t_array[self.index]
        # Select the segment of the full time signal corresponding to the FFT interval
        self.ax_time.plot(self.t_full, self.v_full)
        # Highlight the interval where the FFT was computed
        self.ax_time.axvline(x=t_start, color='g', linestyle='--', label='start fft analysis')
        self.ax_time.axvline(x=t_end, color='r', linestyle='--', label='end fft analysis') 
        # Legend
        self.ax_time.set_title("Velocity over Time")
        self.ax_time.set_xlabel("Time (s)")
        self.ax_time.set_ylabel("Velocity (m/s)")
        self.ax_time.legend()
        self.canvas.draw()
        # Save the figure if data saving is enabled
        if shared.parameters["is_save_data"]:
            # Create a new figure for saving (do not pickle the GUI figure)
            fig_save, (ax_fft_save, ax_time_save) = plt.subplots(1, 2, figsize=(12, 4))
            # FFT
            ax_fft_save.plot(self.freq_array[self.index], self.ffts_array[self.index])
            ax_fft_save.set_title(f"FFT n°{self.index+1}\nIntervalle t={self.t_array[self.index]}")
            ax_fft_save.set_xlabel("Frequency (Hz)")
            ax_fft_save.set_ylabel("Amplitude")
            # temporal signal
            ax_time_save.plot(self.t_full, self.v_full)
            ax_time_save.axvline(x=t_start, color='g', linestyle='--', label='start fft analysis')
            ax_time_save.axvline(x=t_end, color='r', linestyle='--', label='end fft analysis')
            ax_time_save.set_title("Velocity over Time")
            ax_time_save.set_xlabel("Time (s)")
            ax_time_save.set_ylabel("Velocity (m/s)")
            ax_time_save.legend()

            with open(shared.parameters['path_save_data'] + f'\\post_pros_fft_{self.index}.pkl', 'wb') as f:
                pickle.dump(fig_save, f)

            fig_save.savefig(shared.parameters['path_save_data'] + f'\\post_pros_fft_{self.index}.png', dpi=300, bbox_inches='tight')

    def prev_fft(self):
        # Show the previous FFT interval if possible
        if self.index > 0:
            self.index -= 1
            self.plot_fft()

    def next_fft(self):
        # Show the next FFT interval if possible
        if self.index < len(self.ffts_array) - 1:
            self.index += 1
            self.plot_fft()
    
    def on_closing_viewer(self):
        # Properly close the FFT viewer window
        self.destroy()
        tk._default_root.destroy()

