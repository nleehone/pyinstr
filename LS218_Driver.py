from enum import Enum

from driver import *
from processors import *
from validators import *


class LS218_Driver(Driver):
    def __init__(self, resource):
        super().__init__(resource)

    def identification(self):
        return self.query('*IDN?')

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