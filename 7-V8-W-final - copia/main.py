import PyDAQmx as nidaq
import tkinter
from threading import Thread
import numpy as np
import time 
from tkinter.scrolledtext import ScrolledText
from samples import *
from Computation import *
from tunnels_interaction import *
import shared 
from save_data import *
from post_analysis import *
import sys  # Useful for closing the program properly

"""
Main application for the tunnel control system.
"""


# Global Variables
shared.state = 0
shared.tunnel_mode = 0
shared.Sp = 0
# Tunnel variables, initial supposed condition
shared.V = 0                    # m/s
shared.T_amb = 298              # K
shared.P_amb = 100000           # Pa
shared.control_signal = 0       # Control signal for PID algorithm
shared.pid_thread = None        # Thread for PID control
shared.Pressure_pitot = 0       # Pa Pitot pressure 

after_id = None                 # ID for the after method to update gauges. This is used to cancel the update when the window in the graphical interface is closed


def get_state():
    """Get the current state of the system.
    While condition for the PID_RUN function is 1, the system is running.
    Returns:
        int: Current state of the system (1 for running, 0 for stopped).
    """
    return shared.state

def get_Sp():
    """Get the current setpoint speed.
    Returns:
        float: Current setpoint speed (m/s).
    """
    if shared.Sp < 0:
        print("Setpoint cannot be negative, setting to 0")
        shared.Sp = 0 # Prevent negative setpoint
    if shared.Sp > 42:
        shared.Sp = 42 # Prevent setpoint above 42 m/s
        print("Setpoint cannot be above 42 m/s, setting to 42 m/s")
    return shared.Sp

def update_state(Speed, T, cs, p, para):
    """
    Update the shared state variables. Allow the communication between the PID thread and the graphical interface. Save data if enabled.
    Args:
        Speed (float): Current speed (m/s).
        T (float): Current temperature (K).
        cs (float): Current control signal (V).
        p (float): Current pitot pressure (Pa).
        para (dict): Parameters dictionary containing the path to save data and whether to save data.
    Returns:
        None
    """
    shared.V = Speed
    shared.T_amb = T
    shared.control_signal = cs
    shared.Pressure_pitot = p
    if para["is_save_data"]:
        date = time.time() - shared.start_date  # Time since the start of the experiment
        data = [f"{date}, {shared.V}, {shared.Sp}, {shared.T_amb}, {shared.Pressure_pitot}, {shared.P_amb}, {shared.control_signal}\n"]
        save_data(para["path_save_data"]+"\\row_data", data)  # Save data to file

def is_parameter_valid(para):
    """Check if the parameters are valid.
    Args:
        para (dict): Parameters dictionary to validate.
    Returns:
        bool: True if parameters are valid, False otherwise.
        str: Error message if parameters are invalid, empty string otherwise.
    """
    str_error = ""
    if para["mode"] not in [0, 1]:
        str_error = "Invalid mode, must be 0 (small tunnel) or 1 (big tunnel)"
        return False, str_error
    if para["sampling_rate"] < 0:
        str_error ="Sampling rate must be positive"
        return False, str_error
    if para["sampling_batch"] < 0 :
        str_error = "Sampling batch must be positive"
        return False, str_error
    if para["P"] < 0 or para["I"] < 0 or para["D"] < 0:
        str_error = "PID parameters must be non-negative"
        return False, str_error
    return True, str_error

# PID function
def PID_RUN(para):
    """
    PID control loop for the tunnel system.
    This function runs in a separate thread and controls the tunnel based on the PID algorithm. We have a while loop that runs until the state is 0 (stopped). 
    That can happen when the user clicks the stop button or when the maximum time is reached.
    Args:
        para (dict): Parameters dictionary containing PID parameters and other settings.
    Returns:
        int: Returns 0 when the PID control loop is stopped.
    """
    # SECURITY for make dont run for ever
    debut = time.time()
    heure = 0
    # initialization of variables
    Sp = get_Sp()  
    state = get_state()  
    # variables
    e_t = [Sp, Sp, Sp]      # [present time error, previous time error, second previous time error]
    control_signal=0        # Control signal for PID algorithm
    integral_signal=0       # Integral signal for PID algorithm
    temp_1 = 0              # Ensure that in the first iteration we have a density value

    # Send 10V to controller to show range
    if para["mode"] == 1:                                                 # Big tunnel
        print("set range is called")
        set_range_big_tunnel(10) 

    shared.P_amb = sample_pressure(para)                                         # Sample ambient pressure. We assume that the pressure is constant during the PID control loop
    control_signal, integral_signal= PID_Alg(e_t, para, integral_signal)  # Inititate the control signal

    while state == 1:
        heure = time.time() - debut
        # Call the PID algorithm
        control_signal_past = control_signal
        control_signal, integral_signal = PID_Alg(e_t, para, integral_signal)                           # Call the PID algorithm
        control_signal = para["alpha"] * control_signal + (1 - para["alpha"]) * control_signal_past     # Apply a low-pass filter to the control signal for smoother control

        # Give control signal to the tunnel
        write_tunnel(control_signal, para)

        # COMPUTE DENSITY
        if para["is_density_link_temperature"]:                         # Allow to use different model to compute density
            temp = sample_temperature(para)

            if abs(temp - temp_1) > para["beta"] * temp:                # If the temperature has changed significantly, we compute the density
                data_density = compute_density(temp, shared.P_amb, para)
                # Update past temperature
                temp_1 = temp
        else:
            temp = shared.T_amb
            data_density = compute_density(temp, shared.P_amb, para)

        # COMPUTE PRESSURE
        Pressure_pitot = sample_pitot(para)
        
        # Calculating velocity 
        velocity = compute_velocity(Pressure_pitot, data_density)

        # Setting new error
        e_t = [Sp - velocity, e_t[0], e_t[1]]  
        
        # Update the gauges and the state for the graphical interface
        update_state(velocity, temp, control_signal, Pressure_pitot, para)

        # Security check to avoid too long PID loop
        if heure >  para["max_time"]:  # If the time is over, stop the PID
            print_to_tk_terminal("Time is over, stopping PID")
            state_label["text"] = "Off"
            shared.state = 0  # Stop the PID
            # Reset output to 0
            if shared.parameters["mode"] == 1:
                set_range_big_tunnel(0)
            write_tunnel(0, para)
            update_state(0, 300, 0, 0, para)
            break
        # Update the state and Sp for the next iteration
        state = get_state()     # Update state to know if we clicked the stop button
        Sp = get_Sp()           # Update Sp to know if we changed the setpoint speed    
    return 0
    
""" #################################
### Graphical Interface Functions ###
################################# """


# This file contains the functions that interact with the graphical interface
# Fonction pour écrire dans le terminal Tkinter
def print_to_tk_terminal(msg):
    """Print a message to the Tkinter terminal and console.
    Args:
        msg (str): Message to print.
    returns:
        None
    """
    # Get the current time and format it
    date = time.strftime("%H:%M:%S")
    # Insert the message into the terminal in the graphical interface with the current time
    terminal.insert(tkinter.END, str(date)+ "  " + msg + "\n")
    terminal.see(tkinter.END)
    # Print the message to the python console
    print(msg)

def start(para):
    """Start the PID control loop. And initialize the parameters and the data saving if enabled.
    Args:
        para (dict): Parameters dictionary containing PID parameters and other settings.
    Returns:
        None
    """
    # User interface updates
    print_to_tk_terminal("Control Start")  
    print_to_tk_terminal(f"Tunnel will automaticaly shut down in {shared.parameters['max_time']} seconds")
    # Initialize shared variables
    shared.state = 1
    shared.Sp = 0
    # Validate parameters before starting the PID control loop
    boolean, str_error = is_parameter_valid(shared.parameters)
    if not boolean:
        print_to_tk_terminal(f"Invalid parameters: {str_error}")
        raise ValueError(f"Invalid parameters: {str_error}")
    state_label["text"] = "On"
    # Initialize the csv file for saving data if enabled
    if para["is_save_data"]:
        shared.start_date = time.time()                                                     # start time
        para["path_save_data"] = f"experiments\exp_{time.strftime('%Y-%m-%d_%H-%M-%S')}"    # str date for the path for save file
        print_to_tk_terminal("Data saving enabled : path = " + para["path_save_data"])
        save_data_init(para["path_save_data"]+"\\row_data", para)  # Initialize the data file with parameters
    # Start the PID control thread. Useful to run the PID control loop in a separate thread to avoid blocking the GUI.
    shared.pid_thread = Thread(target=PID_RUN, args=(shared.parameters,))
    print_to_tk_terminal("PID thread started")
    shared.pid_thread.start()


def stop(para):
    """ Stop the PID control loop and reset the system.
    Args:
        para (dict): Parameters dictionary containing PID parameters and other settings.
    Returns:
        None
        """
    # User interface updates
    print_to_tk_terminal("Control Stop")
    state_label["text"] = "Off"
    # Set the state to 0 to stop the PID control loop
    shared.state = 0
    shared.pid_thread.join(timeout = 2)         # Wait for the thread to finish (max 2 seconds)
    # Reset tunnel output to 0
    print_to_tk_terminal("Resetting tunnel output to 0")
    if shared.parameters["mode"] == 1:
        set_range_big_tunnel(0)                 # Resetting the range for the big tunnel
    write_tunnel(0, para)
    update_state(0, 298, 0, 0, para)            # Resetting all variables to 0

def change_tunnel_mode():
    """Change the tunnel mode between small and big tunnel.
    This function is called when the user clicks the tunnel mode button.
    It changes the tunnel mode and updates the parameters accordingly.
    If the system is running, it raises an error.
    Args:
        None
    Returns:
        None
    """
    if shared.state == 0:
        if shared.tunnel_mode == 0:
            shared.tunnel_mode = 1
            # Validate parameters before changing
            boolean, str_error = is_parameter_valid(shared.parameters)
            if not boolean:
                raise ValueError(f"Invalid parameters: {str_error}")
            # Change the parameters to the big tunnel parameters
            shared.parameters = shared.parameters_big_tunnel
            # User interface updates
            tunnel_mode_display["text"] = "Current tunnel : Big"
        else:
            shared.tunnel_mode = 0
            # Validate parameters before changing
            boolean, str_error = is_parameter_valid(shared.parameters)
            if not boolean:
                raise ValueError(f"Invalid parameters: {str_error}")
            # Change the parameters to the small tunnel parameters
            shared.parameters = shared.parameters_small_tunnel
            # User interface updates
            tunnel_mode_display["text"] = "Current tunnel : Small"
        print_to_tk_terminal(tunnel_mode_display["text"])
    else:
        # If the system is running, we cannot change the tunnel mode
        print_to_tk_terminal("Changing tunnel mode fail, please press stop buton before if you want to change mode")

def check():
    """Check the speed of the input from the entry box in the graphical interface and update the setpoint speed.
    This function is called when the user clicks the target velocity button.
    It checks the input value, validates it, and updates the setpoint speed accordingly.
    Args:
        None
    Returns:
        int: Returns 1 if the speed is set successfully, 0 if the input is invalid or out of range.
    """
    # Store the user temperature
    Sp_test = entry_box.get()
    # Check if the entry is empty
    if Sp_test == "":
        # For safety reason the speed is set to 0
        shared.Sp = 0
        # User interface updates
        print_to_tk_terminal("Speed is set to 0 m/s")
        return 0
    else:
        try:
            # Check if the entry is a number
            Sp_test = float(Sp_test)
        except ValueError:
            # For safety reason the speed is set to 0
            shared.Sp = 0
            # User interface updates
            print_to_tk_terminal("Invalid input, speed set to 0")
            return 0
    # Check if the entry is greater than 5 ( lower speed possible for the tunnel ) 
    if Sp_test < 5:
        # For safety reason the speed is set to 0
        shared.Sp = 0
        # User interface updates
        print_to_tk_terminal("Speed cannot be below 5 m/s, setting to 0 m/s")
        return 0
    # Check if the entry is lower than 42 ( greater speed possible for the tunnel ) 
    elif Sp_test > 42:
        # For safety reason the speed is set to 0
        shared.Sp = 0
        # User interface updates
        print_to_tk_terminal("Speed cannot be above 42 m/s, setting to 0 m/s")
        return 0
    else:
        # The target speed is set to the user entry stored in the shared.py file
        shared.Sp = Sp_test
        # User interface updates
        print_to_tk_terminal(f"Speed set to {Sp_test} m/s")
        return 1

def toggle_save_data():
    """Change the record mode 
    This function is called when the user clicks the save data button.
    It changes the save mode and updates the parameters accordingly.
    If the system is running, it raises an error.
    Args:
        None
    Returns:
        None"""
    if shared.state == 0:
        # Change update the is_save_data parameters in shared.py file
        shared.parameters["is_save_data"] = not shared.parameters["is_save_data"]
        # User interface updates
        print_to_tk_terminal(f"is_save_data set to {shared.parameters['is_save_data']}")
        save_data_display["text"] = f"{shared.parameters['is_save_data']}"
    else:
        # If the system is running, we cannot change the save mode
        print_to_tk_terminal("Changing record mode fail, please press stop buton before if you want to change mode")

def post_processing():
    """ Post-processing function.
    This function is called when the user clicks the post-processing button.
    First, it computes the interval where the velocity is close to the target velocity.
    Then, it computes an FFT on this interval.
    Finally, it creates a Tkinter interface to display the results.
    Args:
        None
    Returns:
        None """
    # User interface updates
    print_to_tk_terminal("Post Processing button pressed")
    if shared.state == 0:
        if shared.parameters["is_save_data"]:
            # User interface updates
            print_to_tk_terminal("Post processing...")
            # load data from file
            t, v, v_target, T, Pressure_pitot, P_amb, Control_signal, dic_para = load_data(shared.parameters["path_save_data"]+"\\row_data")
            sampling_rate = len(t)/t[-1]                                        # Assuming uniform sampling rate
            # Compute fft
            msg = graph_interface_fft(t, v, sampling_rate, v_target)
            # User interface updates
            print_to_tk_terminal(msg)
        else:
            # If the system dont save the data, we can t compute the post processing
            print_to_tk_terminal("Data is not saved, please enable data saving in the parameters")
    else:
        # If the system is running, we cannot compute the post processing
        print_to_tk_terminal("Post processing fail, please press stop buton before if you want to post process data")

def show_data():
    """
    Show data function.
    This function is called when the user clicks the "Show Data" button.
    If data saving is enabled and the system is stopped, it loads and plots the saved data.
    Otherwise, it displays an appropriate message in the user interface.
    Args:
        None
    Returns:
        None
    """
    # User interface updates
    print_to_tk_terminal("Show Data button pressed")
    if shared.state == 0:
        if shared.parameters["is_save_data"]:
            # User interface updates
            print_to_tk_terminal("Plotting data...")
            # Call the function to plot data
            plot_data(filename=shared.parameters["path_save_data"])
        else:
            # If the system dont save the data, we can t compute the post processing
            print_to_tk_terminal("Data is not saved, please enable data saving in the parameters")
    else:
        # If the system is running, we cannot compute the post processing
        print_to_tk_terminal("Show data fail, please press stop buton before if you want to plot data")

def get_color(val, vmin, vmax):
    """ Return a color between green and red based on the value.
    This function maps a value within a given range to a color gradient from green (minimum) to red (maximum).
    Args:
        val (float): The value to map.
        vmin (float): The minimum value of the range.
        vmax (float): The maximum value of the range.
    Returns:
        str: The corresponding color in hexadecimal format (e.g., '#ff0000').
    """
    ratio = (val - vmin) / (vmax - vmin)
    ratio = max(0, min(ratio, 1))
    # Compute the RGB coef
    r = int(255 * ratio)
    g = int(255 * (1 - ratio))
    b = 0
    return f'#{r:02x}{g:02x}{b:02x}'

def on_closing():
    """ Handle the closing event of the main application window.
    This function is called when the user attempts to close the Tkinter window.
    It safely stops the PID thread, cancels scheduled GUI updates, resets shared variables, and properly closes the application.
    Args:
        None
    Returns:
        None
    """
    global after_id                                 # This variable store the id of process who update the graphical interface
    print("Windows closed")
    shared.state = 0                                # Demande au thread PID de s'arrêter
    if after_id is not None:
        try:
            root.after_cancel(after_id)             # Try to close the process 
        except Exception:
            pass
    if shared.pid_thread is not None and shared.pid_thread.is_alive():
        shared.pid_thread.join(timeout=2)           # Wait the thread to close (max 2 secondes)
    update_state(0, 300, 0, 0, shared.parameters)   # Resetting the variables to 0
    root.destroy()                                  # Close Tkinter window
    tk._default_root.destroy()
    sys.exit(0)                                     # Kill all python program 

def update_gauges():
    """ Update the graphical gauges in the user interface.
    This function updates the speed, temperature, and pitot pressure gauges by drawing colored rectangles
    representing the current values. It is called periodically using Tkinter's after method.
    Args:
        None
    Returns:
        None
    """
    global after_id                             # This variable store the id of process who update the graphical interface
    try:
        # Speed (m/s) gauge as a rectangle
        speed_m_g.delete("all")                                                                 # Kill old data
        speed_m_g.create_text(200, 30, font="Calibri 20 italic bold", text="Speed (m/s)")       # Display "Speed"
        speed_value = max(0, min(shared.V, 42))                                                 # Set the speed value, avoid negative speed and speed greater than 42 
        bar_length = int((speed_value / 42) * 350)                                              # Compute the bar length
        color = get_color(speed_value, 0, 42)                                                   # compute the color of the bar according to the velocity
        speed_m_g.create_rectangle(30, 80, 30 + bar_length, 150, fill=color)                    # Create the colored rectangle
        speed_m_g.create_rectangle(30 + bar_length, 80, 380, 150, fill="gray")                  # Create the grey rectangle 
        speed_m_g.create_text(200, 115, font="Calibri 15 bold", text=f"{round(shared.V,1)} m/s")# Print the current velocity

        # Temperature gauge as a rectangle
        T_amb_g.delete("all")
        T_amb_g.create_text(200, 30, font="Calibri 20 italic bold", text="Temperature (K)")
        temp_value = max(288, min(shared.T_amb, 308))
        bar_length = int(((temp_value - 288) / (308 - 288)) * 350)
        color = get_color(temp_value, 288, 308)
        T_amb_g.create_rectangle(30, 80, 30 + bar_length, 150, fill=color)
        T_amb_g.create_rectangle(30 + bar_length, 80, 380, 150, fill="gray")
        T_amb_g.create_text(200, 115, font="Calibri 15 bold", text=f"{round(shared.T_amb)} K")

        # Pitot Pressure gauge as a rectangle
        P_pitot_g.delete("all")
        P_pitot_g.create_text(200, 30, font="Calibri 20 italic bold", text="Pressure at Pitot Tube (Pa)")
        pitot_value = max(0, min(shared.Pressure_pitot, 100))
        bar_length = int((pitot_value / 100) * 350)
        color = get_color(pitot_value, 0, 100)
        P_pitot_g.create_rectangle(30, 80, 30 + bar_length, 150, fill=color)
        P_pitot_g.create_rectangle(30 + bar_length, 80, 380, 150, fill="gray")
        P_pitot_g.create_text(200, 115, font="Calibri 15 bold", text=f"{round(shared.Pressure_pitot,2)} Pa")

        after_id = root.after(400, update_gauges)
    except tkinter.TclError:
        # Kill window
        pass


# Create Object
root = tkinter.Tk()

# Set window dimension
root.geometry("2000x1000")
# Create the terminal frame for displaying logs and messages
terminal_frame = tkinter.Frame(root)                                                               # the terminal is in the object called root
terminal_frame.grid(row=1, column=3, columnspan=2, rowspan=6, sticky="nsew", padx=10, pady=10)     # Give the position of the terminal in the graphical interface

# Create the scrolled text widget for the terminal output
terminal = ScrolledText(terminal_frame, font="Consolas 12", height=8)
terminal.pack(fill="both", expand=True)

# Create and place the main title label
title = tkinter.Label(root, text="Wind Tunnel Control", font="Calibri 30")
title.grid(row=0, column=2, columnspan=3, pady=20, sticky="nsew")

# Create and place the tunnel mode display label
tunnel_mode_display = tkinter.Label(root, text="Current tunnel : Small", font="Calibri 20")
tunnel_mode_display.grid(row=2, column=7, pady=10)

# Create and place the save data status label
save_data_display = tkinter.Label(root, text=f"{shared.parameters['is_save_data']}", font="Calibri 20")
save_data_display.grid(row=4, column=7, pady=10)

# Create and place the system state label (On/Off)
state_label = tkinter.Label(root, text="Off", font="Calibri 20")
state_label.grid(row=1, column=7, pady=10)

# Create and place the main control buttons
on_button = tkinter.Button(root, text="Start", padx=25, pady=5, fg="white", bg="green", font="Calibri 20", command=lambda: start(shared.parameters))
on_button.grid(row=1, column=6)

off_button = tkinter.Button(root, text="Stop", padx=25, pady=5, fg="white", bg="red", font="Calibri 20", command=lambda: stop(shared.parameters))
off_button.grid(row=1, column=8, pady=10)

tunnel_button = tkinter.Button(root, text="Change mode", padx=25, pady=5, fg="white", bg="grey", font="Calibri 20", command=change_tunnel_mode)
tunnel_button.grid(row=2, column=6, pady=10)

entry_button = tkinter.Button(root, text="Target Velocity", padx=25, pady=5, fg="white", bg="green", font="Calibri 20", command=check)
entry_button.grid(row=3, column=6, pady=10)

save_data_btn = tkinter.Button(root, text=f"Save data", padx=25, pady=5, fg="white", bg="grey", font="Calibri 20", command=toggle_save_data)
save_data_btn.grid(row=4, column=6, pady=10)

show_data_btn = tkinter.Button(root, text="Show Data", padx=25, pady=5, fg="white", bg="orange", font="Calibri 20", command=show_data)
show_data_btn.grid(row=6, column=7, pady=10)

post_processing_btn = tkinter.Button(root, text="Post Processing", padx=25, pady=5, fg="white", bg="purple", font="Calibri 20", command=post_processing)
post_processing_btn.grid(row=6, column=6, pady=10)

# Create the entry box for user to input the target velocity
entry_box = tkinter.Entry(root, font="Calibri 20", width=20)
entry_box.grid(row=3, column=7, pady=10)  # columnspan retiré, ipady possible

# Create the canvas widgets for the gauges (speed, temperature, pressure)
speed_m_g = tkinter.Canvas(root) #, width=400, height=300)
speed_m_g.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

T_amb_g = tkinter.Canvas(root)#, width=400, height=300)
T_amb_g.grid(row=2, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

P_pitot_g = tkinter.Canvas(root)#, width=400, height=300)
P_pitot_g.grid(row=3, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

# Schedule the periodic update of the gauges
root.after(400, update_gauges)

# Set the protocol for closing the window to call the on_closing function
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the Tkinter main event loop
root.mainloop()