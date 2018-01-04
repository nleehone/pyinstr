from LS350_Driver import LS350_Driver

import visa

rm = visa.ResourceManager()
print(rm.list_resources())

LS350 = LS350_Driver(rm.open_resource(''))

LS350.brightness = 10

print(LS350.brightness)