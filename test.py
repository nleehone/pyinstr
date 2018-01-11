from LS350_Driver import LS350_Driver

import visa

from validators import ValidationError

rm = visa.ResourceManager()
#print(rm.list_resources())

res = rm.open_resource('ASRL6::INSTR')
res.data_bits = 7
res.parity = visa.constants.Parity.odd
res.baud_rate = 56000
res.read_termination = '\r\n'

LS350 = LS350_Driver(res)
#print(LS350.identification())

LS350.set_brightness(20)
print(LS350.get_setpoint(2))
LS350.set_setpoint(2, 295)
print(LS350.get_setpoint(2))
#LS350.set_pid(1, 1, 1, 1)
print(LS350.get_ramp_status(1))
print(LS350.get_ramp_parameters(1))
#print(LS350.get_pid(1))
#print(LS350.get_input_curve_number('A'))
print(LS350.get_heater_output(1))
print(LS350.get_curve_header(32))
print(LS350.get_curve_data_point(32, 1))
print(LS350.get_celsius_reading('A'))
print(LS350.get_brightness())