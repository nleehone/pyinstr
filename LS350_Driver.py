from driver import *
from processors import *
from validators import *


class LS350_Driver(Driver):
    def __init__(self, resource):
        super().__init__(resource)

    def identification(self):
        return self.query('*IDN?')

    @Query(processors=[ProcessInteger()])
    def get_brightness(self):
        return self.query('BRIGT?')

    @Write(validators={"contrast": [ValidateRange(1, 32)]})
    def set_brightness(self, contrast):
        self.send("BRIGT {}".format(contrast))

    @Query(validators={"input": [ValidateInArray(['A', 'B', 'C', 'D'])]}, processors=[ProcessReal()])
    def get_celsius_reading(self, input):
        return self.query("CRDG? {}".format(input))

    @Query(validators={"input": [ValidateInArray(['A', 'B', 'C', 'D'])]}, processors=[ProcessReal()])
    def get_kelvin_reading(self, input):
        return self.query("KRDG? {}".format(input))

    @Query(validators={"input": [ValidateInArray(['A', 'B', 'C', 'D'])]}, processors=[ProcessReal()])
    def get_sensor_reading(self, input):
        return self.query("SRDG? {}".format(input))

    @Query(validators={"curve": {ValidateInteger(), ValidateRange(min=1, max=59)}},
           processors=[ProcessCSV(names=('name', 'SN', 'format', 'limit value', 'coefficient'),
                                  processors=(None, None, ProcessInteger(), ProcessReal(), ProcessInteger()))])
    def get_curve_header(self, curve):
        return self.query("CRVHDR? {}".format(curve))

    @Query(validators={"curve": [ValidateInteger(), ValidateRange(min=1, max=59)],
                       "index": [ValidateInteger(), ValidateRange(min=1, max=200)]},
           processors=[ProcessCSV(names=('units value', 'temp value'),
                                  processors=(ProcessReal(), ProcessReal()))])
    def get_curve_data_point(self, curve, index):
        return self.query("CRVPT? {},{}".format(curve, index))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2))]},
           processors=ProcessReal())
    def get_heater_output(self, output):
        return self.query("HTR? {}".format(output))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2))]},
           processors=ProcessInteger())
    def get_heater_status(self, output):
        return self.query("HTRST? {}".format(output))

    @Query(validators={"input": ValidateInArray(('A', 'B', 'C', 'D'))},
           processors=ProcessInteger())
    def get_input_curve_number(self, input):
        return self.query("INCRV? {}".format(input))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))]},
           processors=ProcessCSV(names=("P", "I", "D"),
                                 processors=(ProcessReal(), ProcessReal(), ProcessReal())))
    def get_pid(self, output):
        return self.query("PID? {}".format(output))

    @Write(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))],
                       "p": [ValidateReal(), ValidateRange(min=0, max=9999.9)],
                       "i": [ValidateReal(), ValidateRange(min=0, max=9999.9)],
                       "d": [ValidateReal(), ValidateRange(min=0, max=200)]})
    def set_pid(self, output, p, i, d):
        # TODO: Check if the PID parameters really change beyond p=1000, i=1000 (these are the limits in the manual)
        self.send("PID {},{},{},{}".format(output, p, i, d))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))]},
           processors=ProcessCSV(names=("on/off", "rate value"),
                                 processors=(ProcessInteger(), ProcessReal())))
    def get_ramp_parameters(self, output):
        return self.query("RAMP? {}".format(output))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))]},
           processors=ProcessInteger())
    def get_ramp_status(self, output):
        return self.query("RAMPST? {}".format(output))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))]},
           processors=ProcessInteger())
    def get_heater_range(self, output):
        return self.query("RANGE? {}".format(output))

    @Write(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))],
                       "range": [ValidateInteger(), ValidateRange(min=1, max=5)]})
    def set_heater_range(self, output, range):
        self.send("RANGE {},{}".format(output, range))

    @Query(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))]},
           processors=ProcessReal())
    def get_setpoint(self, output):
        return self.query("SETP? {}".format(output))

    @Write(validators={"output": [ValidateInteger(), ValidateInArray((1, 2, 3, 4))],
                       "value": ValidateReal()})
    def set_setpoint(self, output, value):
        self.send("SETP {},{}".format(output, value))
