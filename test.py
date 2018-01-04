from LS350_Driver import LS350_Driver

import visa

rm = visa.ResourceManager()
print(rm.list_resources())

res = rm.open_resource('ASRL6::INSTR')
res.data_bits = 7
res.parity = visa.constants.Parity.odd
res.baud_rate = 56000

LS350 = LS350_Driver(res)

LS350.brightness = 20

print(LS350.brightness)