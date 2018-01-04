from driver import Driver
from feature import Feature


class LS350_Driver(Driver):
    def __init__(self, resource):
        super().__init__(resource)

    @Feature()
    def identification(self):
        return self.query('*IDN?')

    @Feature()
    def brightness(self):
        return self.query('BRIGT?')

    @brightness.setter
    def brightness(self, val):
        return self.send('BRIGT {}'.format(val))
