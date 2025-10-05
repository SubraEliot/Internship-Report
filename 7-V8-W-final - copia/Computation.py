from math import sqrt
def  PID_Alg(e_t,para, integral_signal):
    """ Compute the PID control signal for the wind tunnel.
    This function calculates the PID (Proportional-Integral-Derivative) control signal
    based on the current and previous errors, the integral signal, and the PID parameters.
    The output is saturated between 0 and 10 volts for safety.
    Args:
        e_t (list): List of errors [current_error, previous_error, error_before_last] in m/s.
        para (dict): Dictionary containing PID parameters ("P", "I", "D", "sampling_batch", "sampling_rate").
        integral_signal (float): The accumulated integral term from previous iterations.
    Returns:
        tuple: (control_signal, integral_signal)
            control_signal (float): The computed control signal (in volts, between 0 and 10).
            integral_signal (float): The updated integral term.
    """
    e_t0 = e_t[0]  # Present error
    e_t1 = e_t[1]  # Error in the last iteration
    e_t2 = e_t[2]  # Error in the iteration before the last

    # Initialize the PID parameters
    P = para["P"]
    I = para["I"]
    D = para["D"]
    # Compute time step
    time_step = (para["sampling_batch"] + 3) / para["sampling_rate"]    # the +3 is a security margin to ensure that the time step is not too small
    #Calculating the control signal
    integral_signal=integral_signal+I*(e_t0+e_t1)*time_step/2
    control_signal=e_t0*P+integral_signal+(e_t0-e_t2)/(2*time_step)*D

    #Saturation of the output control signal to ensure it remains in the 0 to 10 range
    if control_signal>10:
        integral_signal=integral_signal-control_signal+10 #Anti backwip
        control_signal=10

    if control_signal<0:
        control_signal=0

    return control_signal,integral_signal

def  compute_density(temp,p_atm, para):
    """ Compute air density based on air pressure and air temperature.
    This function calculates the air density using the ideal gas law.
    If the temperature sensor is not calibrated, it uses a default temperature value.
    Be careful with the units: pressure (P) must be in Pascals (Pa) and temperature (T) in Kelvin (K).
    Args:
        temp (float): Air temperature in Kelvin.
        p_atm (float): Atmospheric pressure in Pascals.
        para (dict): Dictionary containing parameters, including "is_density_link_temperature".
    Returns:
        float: The computed air density in kg/m^3.
    """
    """
    R=287   #       J/(kg*K) for air, this is the constant of ideal gases in the IS
    if para["is_density_link_temperature"]:
        rho = p_atm/(R*temp)
    else:
        rho = p_atm/(R*(25.0+273)) #While temperature sensor remains uncalibrated use this instead
    return rho
    """
    return 1.2

def compute_velocity(data_pressure,data_density):
    """ Compute air velocity based on air density and pressure difference.
    This function calculates the air velocity using the Bernoulli equation.
    Pressure (P) must be in Pascals (Pa) and density (rho) in kg/m^3.
    If the measured pressure is negative (which can happen at very low velocity), the velocity is set to zero.
    Args:
        data_pressure (float): Pressure difference in Pascals.
        data_density (float): Air density in kg/m^3.
    Returns:
        float: The computed air velocity in m/s.
    """
    if data_pressure<0:
        velocity=0
    else:
        velocity = sqrt(2*data_pressure/data_density)
    return velocity