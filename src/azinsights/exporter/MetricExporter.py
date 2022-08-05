
class MetricExporter:
    def __init__(self):
        pass

    def export(self, data: dict):
        '''Exports metrics collected by a collector.'''
        raise NotImplementedError('Must implement this method')
    