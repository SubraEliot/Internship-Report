import time
import csv
import os

def save_data(filename, data):
    """    Save data to a CSV file.
    This function appends data to a CSV file. Each element in 'data' can be either a string
    (written directly to the file) or a list (written as a CSV row).
    Args:
        filename (str): Name of the file (without '.csv' extension).
        donnees (list): List of lists or strings to save in the file.
    Returns:
        None
    """
    with open(filename + ".csv", 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            # If the row is a string we write it directly (for comments or headers)
            if isinstance(row, str):
                f.write(row)
            else:
                # Otherwise, write the row as a CSV line
                writer.writerow(row)

def save_data_init(filename, dic_para=None):
    """    Initialize the save file with system parameters and headers.
    This function creates (or overwrites) a CSV file, writes experiment metadata (date and parameters)
    as commented header lines, and adds a CSV header for the data columns.
    Args:
        filename (str): Name of the file (without '.csv' extension).
        dic_para (dict, optional): Dictionary of system parameters to record in the header.
    Returns:
        None
    """
    # Ensure the directory exists
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Get the current date and time for experiment metadata
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    header_lines = [
        "### \n",
        f"### Experiment date : {date} \n",
        "### Parameters of the wind tunnel system \n",
        "### \n",
        "\n"
    ]
    # Add each parameter and its value to the header
    for para in dic_para:
        header_lines.append(f"{para} : {dic_para[para]}\n")
    # Write the header lines and section marker to the file (overwrite mode)
    with open(filename + ".csv", 'w', encoding='utf-8') as f:
        for row in header_lines:
            f.write(row)
        f.write("\n### \n### Data \n### \n")
    # Add the CSV column header
    save_data(filename, ["\nt [s], v [m/s], v_target [m/s], T [K], Pressure_pitot [Pa], P_amb [Pa], Control_signal [V]\n"])



