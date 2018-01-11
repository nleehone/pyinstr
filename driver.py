import inspect
from collections import OrderedDict

import time


class Communication(object):
    def validate(self, func, *args):
        signature = inspect.signature(func)

        # Make sure that the inputs are valid
        if self.validators is not None:
            for name, value in zip(signature.parameters.keys(), args):
                validators = self.validators.get(name)
                if validators is None:
                    continue
                try:
                    for validator in validators:
                        validator(value)
                except TypeError:
                    # Validators is not an array
                    validators(value)


class Query(Communication):
    def __init__(self, validators=None, processors=None):
        self.processors = processors
        self.validators = validators

    def __call__(self, func):
        def query(*args):
            self.validate(func, args)

            # Run the query function
            val = func(*args)

            # Process the output
            if self.processors is not None:
                try:
                    for processor in self.processors:
                        val = processor(val)
                except TypeError:
                    # Processor is a single element
                    val = self.processors(val)
            return val
        return query


class Write(Communication):
    def __init__(self, validators=None):
        self.validators = validators

    def __call__(self, func):
        def write(*args):
            self.validate(func, args)

            # Write the data to the instrument
            func(*args)
        return write


class DriverMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.query_commands = [value for value in namespace.values() if isinstance(value, Query)]
        for query_command in cls.query_commands:
            query_command.instance = cls


class Driver(object):
    def __init__(self, resource):
        self.wait_time = 0.06 # TODO: Check why we need 0.06s instead of 0.05s delay for LS350
        self.instrument = resource

        self.query_commands = [value for value in self.__dict__.keys() if isinstance(value, Query)]
        for query_command in self.query_commands:
            query_command.instance = self

    def query(self, query_string):
        val = self.instrument.query(query_string)
        time.sleep(self.wait_time)
        return val

    def send(self, message):
        self.instrument.write(message)
        time.sleep(self.wait_time)