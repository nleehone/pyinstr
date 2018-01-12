from time import time, strftime
import numpy as np

import logging

import nidaqmx
import visa
from nidaqmx import task
from nidaqmx.constants import AcquisitionType, TerminalConfiguration

from LS350_Driver import LS350_Driver

rm = visa.ResourceManager()
print(rm.list_resources())

# ----------------------------------
# Configuration. Set parameters here
# ----------------------------------
filename = 'ASY-1212A_Test1_ThermalCycling_Run1.dat'
T_room = 25
He_flow = 40  # mbar
T_range = 0.2
ramp_rate = 10  # 10 K/minute
settle_time = 30  # seconds
timeout = 600  # seconds

VTI_T_diff = 0  # K

LS350_address = 'GPIB0::12::INSTR'
VTI_input = 'A'
sample_input = 'B'
VTI_output = 1
sample_output = 2

log_filename = '{}.log'.format(filename.split('.')[0])
logging.basicConfig(filename=log_filename, format='%(asctime)s.%(msecs)03d:%(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)


res = rm.open_resource(LS350_address)
res.data_bits = 7
res.parity = visa.constants.Parity.odd
res.baud_rate = 56000
res.read_termination = '\r\n'
LS350 = LS350_Driver(res)

print(LS350.identification())


task = nidaqmx.Task()
task.ai_channels.add_ai_voltage_chan('Dev1/ai29', terminal_config=TerminalConfiguration.RSE, min_val=-10, max_val=10)
task.ai_channels.add_ai_voltage_chan('Dev1/ai21', terminal_config=TerminalConfiguration.RSE, min_val=-10, max_val=10)
task.timing.cfg_samp_clk_timing(rate=1000, sample_mode=AcquisitionType.FINITE, samps_per_chan=100)

file = open(filename, 'w', buffering=1)
file.write('FILENAME: {}\n'.format(filename))
file.write('DATETIME: {}\n'.format(strftime("%c")))
file.write('SETUP: Ramp Rate={} C/minute\n'.format(ramp_rate))
file.write('SETUP: Temperature settle range=+/-{} C\n'.format(T_range))
file.write('SETUP: He flow {} mba\n'.format(He_flow))
file.write('SETTINGS:\n')
file.write('SAMPLE_INPUT: {}\n'.format(sample_input))
file.write('SAMPLE_OUTPUT: {}\n'.format(sample_output))
file.write('VTI_INPUT: {}\n'.format(VTI_input))
file.write('VTI_OUTPUT: {}\n'.format(VTI_output))
file.write('VTI_PID: {}\n'.format(LS350.get_pid(VTI_output)))
file.write('SAMPLE_PID: {}\n'.format(LS350.get_pid(sample_output)))
file.write('\n')
file.write('DATA:\n')
file.write('Time,VTI Setpoint (C),VTI Temperature (C),VTI Sensor (Ohm),Sample Setpoint (C),Sample Temperature (C),Sample Sensor (Ohm),Pressure1 (mbar),Pressure2 (mbar)\n')


def measure_temperature(write=False):
    T_VTI = LS350.get_celsius_reading(VTI_input)
    S_VTI = LS350.get_sensor_reading(VTI_input)

    setp_VTI = LS350.get_setpoint_celsius(VTI_output)

    T_samp = LS350.get_celsius_reading(sample_input)
    S_samp = LS350.get_sensor_reading(sample_input)

    setp_samp = LS350.get_setpoint_celsius(sample_output)

    try:
        p1, p2 = task.read(number_of_samples_per_channel=100)
        p1 = np.mean(p1) * 1.33322 * 1
        p2 = np.mean(p2) * 1.33322 * 100
    except Exception:
        p1 = p2 = -1

    if write:
        file.write('{},{},{},{},{},{},{},{},{}\n'.format(time(), setp_VTI, T_VTI, S_VTI, setp_samp, T_samp, S_samp, p1, p2))

    return time(), setp_VTI, T_VTI, S_VTI, setp_samp, T_samp, S_samp, p1, p2


def set_temperature_and_settle(T_VTI, T_samp, T_range, settle_time, timeout, record=False):
    LS350.set_setpoint_celsius(VTI_output, T_VTI)
    LS350.set_setpoint_celsius(sample_output, T_samp)

    timer = time()
    settled_timer = time()

    settled = False

    while True:
        if timeout < time() - timer:
            logging.warning(
                'Reached timeout! Possible Causes: timeout may be too small, heater power not set correctly, wrong flow rate.')
            break

        _, setp_VTI, T_VTI, S_VTI, setp_samp, T_samp, S_samp, p1, p2 = measure_temperature(record)

        ramp_status = LS350.get_ramp_status()

        if ramp_status != 0:
            logging.info('Timer reset because ramp still ongoing.')
            settled_timer = time()
        elif abs(setp_samp - T_samp) <= T_range:
            if settle_time < time() - settled_timer:
                settled = True
                break
        else:
            # Reset the timer if the temperature is out of range
            logging.info(
                'Timer reset because temperature out of range: T_set={}, T_curr={}, T_range={}'.format(setp_samp, T_samp,
                                                                                                       T_range))
            settled_timer = time()

    return settled, time() - timer


def close():
    global rm

    LS350.instrument.close()
    del LS350.instrument

    rm.close()
    del rm

    task.close()

# ------------------------------------------------
# Measurement protocol
# ------------------------------------------------

# Step: Set temperature to room temperature
# -----------------------------------------
print("Set temperature to room temperature")

logging.info('Ramp rate set to None for fast ramp')
LS350.set_setpoint_ramping_off(VTI_output)
LS350.set_setpoint_ramping_off(sample_output)

logging.info('Set temperature to {} C and wait for settle'.format(T_room))
file.write("INFO: Settle room temperature BEGIN\n".format(T_room))
settled, timer = set_temperature_and_settle(T_room, T_room, T_range, settle_time, timeout, record=False)
if not settled:
    logging.error('Could not set the temperature to {} C. Check the flow rate and heater power.'.format(T_room))
    close()
    file.close()
    exit(1)
else:
    logging.info('Settled at {} C in {} seconds'.format(T_room, timer))
file.write("INFO: Settle room temperature END\n".format(T_room))


T_set = -95

for i in range(2):
    print("Starting cycle {}".format(i))
    file.write('INFO: Cycle {} BEGIN\n'.format(i))

    # Step: Ramp to T_set and then settle there
    # -----------------------------------------
    print("Ramp to T_set and then settle there")
    LS350.set_setpoint_ramping_off(VTI_output)
    logging.info('Sample ramp rate set to {} C/minute'.format(ramp_rate))
    LS350.set_setpoint_ramp_parameters(sample_output, 1, ramp_rate)

    logging.info('Set temperature to {} C and wait for settle'.format(T_set))
    file.write('INFO: Ramp BEGIN\n')  # Split the data file
    settled, timer = set_temperature_and_settle(T_set - VTI_T_diff, T_set, T_range, settle_time, 3600, record=True)
    if not settled:
        logging.error('Could not set the temperature to {} C. Check the flow rate and heater power.'.format(T_room))
        close()
        file.close()
        exit(1)
    else:
        logging.info('Settled at {} C in {} seconds'.format(T_set, timer))
    file.write('INFO: Ramp END\n')  # Split the data file

    # Step: Soak for wait_time at T_set
    # -----------------------------------------
    print("Soak at T_set for 1 hour")
    wait_time = 3600
    file.write('INFO: Soak BEGIN\n')

    t1 = time()
    while time() - t1 < wait_time:
        measure_temperature(True)
    file.write('INFO: Soak END\n')

    # Step: Ramp to room temperature and then settle there
    # -----------------------------------------
    print("Ramp to room temperature and then settle there")
    LS350.set_setpoint_ramping_off(VTI_output)
    logging.info('Sample ramp rate set to {} C/minute'.format(ramp_rate))
    LS350.set_setpoint_ramp_parameters(sample_output, 1, ramp_rate)

    logging.info('Set temperature to {} C and wait for settle'.format(T_room))
    file.write('INFO: Ramp BEGIN\n')  # Split the data file
    settled, timer = set_temperature_and_settle(T_room, T_room, T_range, settle_time, 3600, record=True)
    if not settled:
        logging.error('Could not set the temperature to {} C. Check the flow rate and heater power.'.format(T_room))
        close()
        file.close()
        exit(1)
    else:
        logging.info('Settled at {} C in {} seconds'.format(T_room, timer))
    file.write('INFO: Ramp END\n')  # Split the data file

    # Step: Soak for wait_time at room temperature
    # -----------------------------------------
    print("Soak at room temperature for 1 hour")
    wait_time = 3600
    file.write('INFO: Soak BEGIN\n')

    t1 = time()
    while time() - t1 < wait_time:
        measure_temperature(True)
    file.write('INFO: Soak END\n')

    file.write('INFO: Cycle {} END\n'.format(i))

close()