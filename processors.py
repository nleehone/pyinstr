class ProcessorError(Exception):
    pass


class Processor(object):
    def __init__(self):
        pass


class ProcessInteger(Processor):
    def __init__(self):
        super().__init__()

    def __call__(self, value):
        try:
            result = int(value)
        except Exception as e:
            raise ProcessorError("Could not convert {} into an integer".format(value)) from e
        return result


class ProcessReal(Processor):
    def __init__(self):
        super().__init__()

    def __call__(self, value):
        try:
            result = float(value)
        except Exception as e:
            raise ProcessorError("Could not convert {} into a Real".format(value)) from e
        return result


class ProcessCSV(Processor):
    def __init__(self, names, processors=None, strip=True):
        super().__init__()
        self.strip = strip
        self.param_names = names
        self.processors = processors

    def __call__(self, value):
        values = value.split(',')
        result = {}
        for i, (name, val) in enumerate(zip(self.param_names, values)):
            if self.strip:
                val = val.strip()
            if self.processors is not None:
                try:
                    for processor in self.processors[i]:
                        val = processor(val)
                except TypeError:
                    # Catch if processors[i] is not iterable (i.e. there is a single processor)
                    if self.processors[i] is not None:
                        val = self.processors[i](val)
            result[name] = val
        return result