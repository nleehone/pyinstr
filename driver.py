class Driver(object):
    def __init__(self, resource):
        self.instrument = resource

    def query(self, query_string):
        return self.instrument.query(query_string)

    def send(self, message):
        self.instrument.write(message)