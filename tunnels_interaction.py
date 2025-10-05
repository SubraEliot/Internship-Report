import nidaqmx as nidaq
def write_tunnel(value, para):
    if para["mode"] == 1:  # Big tunnel
        with nidaq.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev2/ao1')
            task.write(value)
    elif para["mode"] == 0: # Small tunnel
        with nidaq.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            value=value/1.013-0.0997/1.013 # Correcting the bias for the small tunnel
            task.write(value)
    else:
        raise ValueError("In write_tunnel() tunnel mode need to be equal to : \n 1 : for the big tunnel \n 0 : for the small tunnel")
    return

def set_range_big_tunnel(value):
    with nidaq.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev2/ao0')
        task.write(value)

