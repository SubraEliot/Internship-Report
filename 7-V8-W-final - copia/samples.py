import PyDAQmx as nidaq
import numpy as np

#This function samples the ambient pressure 
def sample_pressure(para):
    """    Sample the ambient pressure using a DAQ device.
    This function configures the appropriate analog input channel based on the tunnel mode,
    sets the sampling rate and batch size, acquires a batch of voltage samples, averages them,
    and converts the result to a physical pressure value using calibration parameters.
    Args:
        para (dict): Dictionary containing acquisition parameters and calibration coefficients.
            - "mode": Tunnel mode (0 = small tunnel, 1 = big tunnel)
            - "sampling_rate": Sampling rate in Hz
            - "sampling_batch": Number of samples to acquire
            - "factor_conv": Multiplicative calibration factor for pressure
            - "offset_atm": Additive offset for pressure calibration
            - "k_atm": Gain for pressure calibration
    Returns:
        float: The measured ambient pressure in Pascals.
    """
    pa = nidaq.Task()
    #P Select the correct analog input channel based on tunnel mode
    if para["mode"] == 1:
        pa.CreateAIVoltageChan("Dev2/ai2", "pressure", nidaq.DAQmx_Val_RSE, 0, 5, nidaq.DAQmx_Val_Volts, None)
    elif para["mode"] == 0:
        pa.CreateAIVoltageChan("Dev1/ai6", "pressure", nidaq.DAQmx_Val_RSE, 0, 10, nidaq.DAQmx_Val_Volts, None)
 
    #Establish sampling rate
    pa.CfgSampClkTiming("", para["sampling_rate"], nidaq.DAQmx_Val_Rising, nidaq.DAQmx_Val_FiniteSamps, para["sampling_batch"])
    #Reserve memory
    data = np.zeros((para["sampling_batch"],), dtype=np.float64)
    #Sample
    read = nidaq.int32()
    pa.ReadAnalogF64(para["sampling_batch"], (para["sampling_batch"]+2)/para["sampling_rate"], nidaq.DAQmx_Val_GroupByChannel,
        data, len(data), nidaq.byref(read), None)
    # Average the sample
    v_pressure=np.mean(data, dtype=np.float64)
    # Convert the averaged voltage to physical pressure using calibration parameters
    p_atm=para["factor_conv"]*para["offset_atm"]+v_pressure*para["k_atm"]
    return p_atm

def sample_temperature(para):
    """    Sample the air temperature using a DAQ device.
    This function configures the appropriate analog input channel based on the tunnel mode,
    sets the sampling rate and batch size, acquires a batch of voltage samples, averages them,
    and converts the result to a physical temperature value (in Kelvin) using calibration parameters.
    Args:
        para (dict): Dictionary containing acquisition parameters and calibration coefficients.
            - "mode": Tunnel mode (0 = small tunnel, 1 = big tunnel)
            - "sampling_rate": Sampling rate in Hz
            - "sampling_batch": Number of samples to acquire
            - "offset_T": Additive offset for temperature calibration
            - "k_T": Gain for temperature calibration
    Returns:
        float: The measured air temperature in Kelvin.
    """
    t = nidaq.Task()
    # Select the correct analog input channel based on tunnel mode
    if para["mode"] == 1:  # Big tunnel
        t.CreateAIVoltageChan("Dev2/ai1", "temperature", nidaq.DAQmx_Val_RSE, 0, 10, nidaq.DAQmx_Val_Volts, None)
    elif para["mode"] == 0:  # Small tunnel
        t.CreateAIVoltageChan("Dev1/ai5", "temperature", nidaq.DAQmx_Val_RSE, 0, 10, nidaq.DAQmx_Val_Volts, None)
    # Establish sampling rate
    t.CfgSampClkTiming("", para["sampling_rate"], nidaq.DAQmx_Val_Rising, nidaq.DAQmx_Val_FiniteSamps, para["sampling_batch"])
    # Reserve memory
    data = np.zeros((para["sampling_batch"],), dtype=np.float64)
    # Acquire the samples from the DAQ device
    read = nidaq.int32()
    t.ReadAnalogF64(para["sampling_batch"], (para["sampling_batch"]+2)/para["sampling_rate"], nidaq.DAQmx_Val_GroupByChannel,
        data, len(data), nidaq.byref(read), None)
    # Average the sample
    v_temp=np.mean(data, dtype=np.float64)
    # Convert the averaged voltage to physical temperature using calibration parameters
    temp=para["offset_T"]+para["k_T"]*v_temp+273.15
    return temp

def sample_pitot(para):
    """    Sample the pitot tube pressure using a DAQ device.
    This function configures the appropriate analog input channel based on the tunnel mode,
    sets the sampling rate and batch size, acquires a batch of voltage samples, averages them,
    and converts the result to a physical pressure value using calibration parameters.
    Args:
        para (dict): Dictionary containing acquisition parameters and calibration coefficients.
            - "mode": Tunnel mode (0 = small tunnel, 1 = big tunnel)
            - "sampling_rate": Sampling rate in Hz
            - "sampling_batch": Number of samples to acquire
            - "k_pitot": Gain for pitot pressure calibration
            - "offset_pitot": Additive offset for pitot pressure calibration
    Returns:
        float: The measured pitot pressure in Pascals.
    """
    pi = nidaq.Task()
    # Select the correct analog input channel based on tunnel mode
    if para["mode"] == 1:  # Big tunnel
        pi.CreateAIVoltageChan("Dev2/ai3", "pressure", nidaq.DAQmx_Val_RSE, 0, 10, nidaq.DAQmx_Val_Volts, None)
    elif para["mode"] == 0:  # Small tunnel
        pi.CreateAIVoltageChan("Dev1/ai4", "pressure", nidaq.DAQmx_Val_RSE, 0, 10, nidaq.DAQmx_Val_Volts, None)
    # Establish sampling rate
    pi.CfgSampClkTiming("", para["sampling_rate"], nidaq.DAQmx_Val_Rising, nidaq.DAQmx_Val_FiniteSamps, para["sampling_batch"])
    # Reserve memory
    data = np.zeros((para["sampling_batch"],), dtype=np.float64)
    # Acquire the samples from the DAQ device
    read = nidaq.int32()
    pi.ReadAnalogF64(para["sampling_batch"], (para["sampling_batch"]+2)/para["sampling_rate"], nidaq.DAQmx_Val_GroupByChannel,
        data, len(data), nidaq.byref(read), None)
    
    # Average the sampled voltages
    v_pitot=np.mean(data, dtype=np.float64)
    print(v_pitot)
    # Convert the averaged voltage to physical pitot pressure using calibration parameters
    data_pressure=para["k_pitot"]*v_pitot+para["offset_pitot"] 
    #print(v_pitot)
    return data_pressure
