from collector.PrometheusMetricCollector import PrometheusMetricCollector

import logging

logger = logging.getLogger(__name__)


class MetricCollectorFactory:
    '''Class used to instantiate children of MetricCollector'''
    @staticmethod
    def Factory(collector_type: str = 'Prometheus'):
        '''Provides instance of a certain collector type.

        Parameters
        ----------
        collector_type : str
            A string representing the name of the metric collector

        Returns
        -------
        MetricCollector
            An instance of a subclass of MetricCollector

        '''
        logger.debug('Factory')
        collectors = {
            'Prometheus': PrometheusMetricCollector
        }
        if collector_type not in collectors:
            raise Exception('{0} is not a known collector in MetricCollectorFactory.'.format(collector_type))
        return collectors[collector_type]()
