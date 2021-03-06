"""
The Feature class implements getter and setter functions that can check their type and process parameters.

When a Feature is initialized (__init__) it creates two function slots to store the getter (fget) and setter (fset)
The Feature is first called (__call__) during decoration. This specifies the getter function
    @Feature()
    def feature_name(self):
        ...

After this, a setter function can be added by either calling the Feature again, or calling its setter:
    @feature_name
    def setter(self, val):
        ...

    @feature_name.setter
    def setter(self, val):
        ...

When the getter is called (e.g. print(feature_name)), the __get__ function is called which uses the fget function
to execute the action.

When the setter is called (e.g. feature_name = 10), the __set__ function is called which uses the fset function to
execute the action.
"""


class Feature(object):
    def __init__(self):
        self.fget = None  # Getter function
        self.fset = None  # Setter function

        self.get_validators = []
        self.set_validators = []

    def __call__(self, func):
        if self.fget is None:
            return self.getter(func)

    def getter(self, func):
        self.fget = func
        return self

    def setter(self, func):
        self.fset = func
        return self

    def __get__(self, instance, owner):
        for validator in self.set_validators:
            validator.validate()

        value = self.fget(instance)
        for processor in self.get_processors:
            value = processor.process(value)
        return value

    def __set__(self, instance, value):
        for validator in self.set_validators:
            validator.validate(value)

        return self.fset(instance, value)