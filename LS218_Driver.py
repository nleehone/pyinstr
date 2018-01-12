from enum import Enum

from driver import *
from processors import *
from validators import *


class LS218_Driver(Driver):
    def __init__(self, resource):
        super().__init__(resource)

    def identification(self):
        return self.query('*IDN?')

    def clear_interface(self):
        return self.write("*CLS")

    def reset_instrument(self):
        self.write("*RST")

    @NotSupported('This command is not supported in the Model 218.')
    def wait_to_continue(self):
        self.write("*WAI")

    @Query(processors=ProcessInteger())
    def self_test(self):
        return self.query("*TST?")

    @Write(validators={'input': (ValidateInteger(), ValidateRange(min=1, max=8)),
                       'off_on': ValidateInArray((0, 1)),
                       'source': ValidateInArray((1, 2, 3, 4)),
                       'high_value': ValidateReal(),
                       'low_value': ValidateReal(),
                       'deadband': ValidateReal(),
                       'latch_enable': ValidateInArray((0, 1))
                       })
    def set_input_alarm_parameters(self, input, off_on, source, high_value, low_value, deadband, latch_enable):
        self.send("ALARM {input},{off_on},{source},{high_value},{low_value},{deadband},{latch_enable}".format(
            input=input, off_on=off_on, source=source, high_value=high_value, low_value=low_value, deadband=deadband,
            latch_enable=latch_enable))

    @Query(validators={'input': (ValidateInteger(), ValidateRange(min=1, max=8))},
           processors=ProcessCSV(names=('off_on', 'source', 'high value', 'low value',
                                        'deadband', 'latch enable'),
                                 processors=(ProcessInteger(), ProcessInteger(), ProcessReal(), ProcessReal(),
                                             ProcessReal(), ProcessInteger())))
    def get_input_alarm_parameters(self, input):
        return self.query("ALARM? {}".format(input))

    @Query(validators={'input': (ValidateInteger(), ValidateRange(min=1, max=8))},
           processors=ProcessCSV(names=('high status', 'low_status'), processors=(ProcessInteger(), ProcessInteger())))
    def get_input_alarm_status(self, input):
        return self.query("ALARMST? {}".format(input))

    @Write(validators={"on_off": ValidateInArray((0, 1))})
    def set_audible_alarm_state(self, on_off):
        self.send("ALMB {}".format(on_off))

    @Query(processors=ProcessInteger())
    def get_audible_alarm_state(self):
        return self.query("ALMB?")

    def reset_latched_audible_alarms(self):
        self.send("ALMRST")

    @Write(validators={'output': ValidateInArray((1, 2)),
                       'bipolar_enable': ValidateInArray((0, 1)),
                       'mode': ValidateInArray((0, 1, 2)),
                       'input': (ValidateInteger(), ValidateRange(min=1, max=8)),
                       'source': ValidateInArray((1, 2, 3, 4)),
                       'high_value': ValidateReal(),
                       'low_value': ValidateReal(),
                       'manual_value': ValidateReal()})
    def set_analog_output_parameters(self, output, bipolar_enable, mode, input, source, high_value, low_value, manual_value):
        self.send("ANALOG {},{},{},{},{},{},{},{}".format(output, bipolar_enable, mode, input, source, high_value, low_value, manual_value))

    @Query(validators={'output': ValidateInArray((1, 2))},
           processors=ProcessCSV(names=('bipolar enable', 'mode', 'input', 'source',
                                        'high value', 'low value', 'manual value'),
                                 processors=(ProcessInteger(), ProcessInteger(), ProcessInteger(), ProcessInteger(),
                                             ProcessReal(), ProcessReal(), ProcessReal())))
    def get_analog_output_parameters(self, output):
        return self.query("ANALOG? {}".format(output))

    @Query(validators={'output': ValidateInArray((1, 2))},
           processors=ProcessReal())
    def get_analog_output(self, output):
        return self.query("AOUT? {}".format(output))

    @Write(validators={"bps": ValidateInArray((0,1,2))})
    def set_baud_rate(self, bps):
        """
        :param bps:
        0 = 300
        1 = 1200
        2 = 9600
        """
        self.write("BAUD {}".format(bps))

    @Query(processors=ProcessInteger())
    def get_baud_rate(self):
        """
        0 = 300
        1 = 1200
        2 = 9600
        """
        return self.query("BAUD?")

    @Query(validators={"input": (ValidateInteger(), ValidateRange(min=1, max=8))},
           processors=ProcessReal())
    def get_celsius_reading(self, input):
        return self.query("CRDG? {}".format(input))

    @Query(validators={"input": (ValidateInteger(), ValidateRange(min=1, max=8))},
           processors=ProcessReal())
    def get_kelvin_reading(self, input):
        return self.query("KRDG? {}".format(input))

    @Query(validators={"input": (ValidateInteger(), ValidateRange(min=1, max=8))},
           processors=ProcessReal())
    def get_sensor_reading(self, input):
        return self.query("SRDG? {}".format(input))

    @Query(processors=ProcessCSV(names=('input 1', 'input 2', 'input 3', 'input 4', 'input 5', 'input 6', 'input 7', 'input 8')))
    def get_celsius_reading_all(self):
        return self.query("CRDG? 0")

    @Query(processors=ProcessCSV(
        names=('input 1', 'input 2', 'input 3', 'input 4', 'input 5', 'input 6', 'input 7', 'input 8')))
    def get_kelvin_reading_all(self):
        return self.query("KRDG? 0")

    @Query(processors=ProcessCSV(
        names=('input 1', 'input 2', 'input 3', 'input 4', 'input 5', 'input 6', 'input 7', 'input 8')))
    def get_sensor_reading_all(self):
        return self.query("SRDG? 0")

    @Write(validators={'input': (ValidateInteger(), ValidateRange(min=1, max=8))})
    def delete_user_curve(self, input):
        # Curves 21-28 are the user curves, so add 20 to the input number to select which to delete
        self.send("CRVDEL {}".format(input + 20))