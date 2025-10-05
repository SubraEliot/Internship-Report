""" #############
### shared.py ###
#############"""
"""This file contains shared variables and parameters used across different modules in the project."""
import time

state = 0
tunnel_mode = 0
Sp = 0  

# Expected values for the variables at the beginning
# These values are used to initialize the system and should be updated as needed
V = 0 # m/s
T_amb = 300  # K
P_amb = 100000  # Pa
control_signal = 0  # V
pid_thread = None
Pressure_pitot = 0  # Pa
start_date = 0

"""
mode : 0 for small tunnel, 1 for big tunnel
is_save_data : Boolean to save data in a file
path_save_data : Path to save data file
is_density_link_temperature : Boolean Temperature for density calculation, in Kelvin
alpha : Sensibility factor
beta : Temperature sensibility
sampling_rate : sampling rate in Hz
sampling_batch_temp : Amount of samples that we promediate for every temperature measure that would be taken for every cycle
sampling_batch_pitot : Amount of samples that we promediate for every point of pitot data that would be taken for every cycle
k_pitot : K = 106.044  # Constante calibracion Validyne OLD, K=88.618 marcos
offset_pitot : offset Pitot, seems to be in mmHg, not in pascal or mmH2O, if changed check sample_pitot function
offset_T : offset Temperature 
k_T : Constante calibracion temperature
k_atm : Constante calibracion presion, Seems to be in mmHg, not in pascal or mmH2O, if changed check sample_pressure function
offser_atm : offset presion, Seems to be in mmHg, not in pascal or mmH2O, if changed check sample_pressure function
factor_conv : Conversion from electric magnitude to real pressure 
P : P parameter for PID algorithm
I : I parameter for PID algorithm
D : D parameter for PID algorithm
"conv_factor" : Convergence factor use for the computation PID convergence in the post analysis 
"""
parameters_big_tunnel = {"mode" : 1, "max_time" : 1800, "is_save_data" : True, "path_save_data" : f"experiments\exp_{time.strftime('%Y-%m-%d_%H-%M-%S')}","is_density_link_temperature" : False, "alpha" : 0.1, "beta" : 0.02, "sampling_rate" : 1000, "sampling_batch" : 400,
                        "k_pitot" : 86.328, "offset_pitot" : 0,"offset_T" : -0.146, "k_T" : 100, "k_atm" : 41286, "offset_atm" : 85343, "factor_conv" : 1, "P" : 0.12, "I" : 0.015, "D" : 0.075, "conv_factor" : 0.05}
parameters_small_tunnel = {"mode" : 0, "max_time" : 400,"is_save_data" : True, "path_save_data" : f"experiments\exp_{time.strftime('%Y-%m-%d_%H-%M-%S')}","is_density_link_temperature" : False, "alpha" : 0.1, "beta" : 0.02, "sampling_rate" : 1000, "sampling_batch" : 400,
                        "k_pitot" : 60, "offset_pitot" : -1, "offset_T" : -0.146, "k_T" : 100, "k_atm" : 45, "offset_atm" : 599.8, "factor_conv" : 101325/760, "P" : 0.13, "I" : 0.05, "D" : 0.05, "conv_factor" : 0.05}

parameters = parameters_small_tunnel  # Default to small tunnel parameters


"""
-- - 16-07-2025: parameters_big_tunnel = {"mode" : 1, "max_time" : 1800, "is_save_data" : True, "path_save_data" : f"experiments\exp_{time.strftime('%Y-%m-%d_%H-%M-%S')}","is_density_link_temperature" : False, "alpha" : 0.1, "beta" : 0.02, "sampling_rate" : 1000, "sampling_batch" : 400,
                        "k_pitot" : 86.207, "offset_pitot" : 0,"offset_T" : -0.146, "k_T" : 100, "k_atm" : 5200, "offset_atm" : 80000, "factor_conv" : 1, "P" : 0.12, "I" : 0.015, "D" : 0.075, "conv_factor" : 0.05}

16-07-2025 - --- parameters_big_tunnel = {"mode" : 1, "max_time" : 1800, "is_save_data" : True, "path_save_data" : f"experiments\exp_{time.strftime('%Y-%m-%d_%H-%M-%S')}","is_density_link_temperature" : False, "alpha" : 0.1, "beta" : 0.02, "sampling_rate" : 1000, "sampling_batch" : 400,
                        "k_pitot" : 86.328, "offset_pitot" : 0,"offset_T" : -0.146, "k_T" : 100, "k_atm" : 41286, "offset_atm" : 85343, "factor_conv" : 1, "P" : 0.12, "I" : 0.015, "D" : 0.075, "conv_factor" : 0.05}

                        """