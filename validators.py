class ValidationError(Exception):
    pass


class Validator(object):
    pass


class ValidateInteger(Validator):
    def __init__(self):
        super().__init__()

    def __call__(self, value):
        if not isinstance(value, int):
            raise ValidationError("The input must be an integer, but instead got {} of type {}".format(value, type(value)))


class ValidateReal(Validator):
    def __init__(self):
        super().__init__()

    def __call__(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise ValidationError("The input must be a Real, but instead got {} of type {}".format(value, type(value)))


class ValidateRange(Validator):
    def __init__(self, min=None, max=None):
        super().__init__()
        self.min = min
        self.max = max

    def __call__(self, value):
        if self.max is not None and value > self.max:
                raise ValidationError("The input {} must be <= {}".format(value, self.max))
        if self.min is not None and value < self.min:
                raise ValidationError("The input {} must be >= {}".format(value, self.min))


class ValidateInArray(Validator):
    def __init__(self, array):
        super().__init__()
        self.array = array

    def __call__(self, value):
        if value not in self.array:
            raise ValidationError("The input {} must be one of {}".format(value, self.array))