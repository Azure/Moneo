class MetricExporter:
    '''Abstract class meant to receive metrics from a collector and send them elsewhere.'''

    def __init__(self):
        pass

    def export(self, data: dict):
        '''Exports metrics collected by a collector.'''
        raise NotImplementedError('Must implement this method')
