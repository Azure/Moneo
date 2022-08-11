class MetricCollector:
    '''Abstract class meant to collect metrics internally from some resource to later expose it to an exporter.'''

    def __init__(self):
        pass

    def collect_metrics(self):
        '''Collects metrics internally.'''
        raise NotImplementedError('Must implement this method')
    
    def get_current_results():
        '''Exposes metrics such that they may be consumed by an exporter.'''
        raise NotImplementedError('Must implement this method')

