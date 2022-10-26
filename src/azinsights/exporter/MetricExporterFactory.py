from exporter.ApplicationInsightsExporter import ApplicationInsightsExporter

import logging

logger = logging.getLogger(__name__)


class MetricExporterFactory:
    '''Class used to instantiate children of MetricExporter'''
    @staticmethod
    def Factory(exporter_type: str = 'ApplicationInsights'):
        '''Provides instance of a certain exporter type.

        Parameters
        ----------
        exporter : str
            A string representing the name of the metric exporter

        Returns
        -------
        MetricExporter
            An instance of a subclass of MetricExporter

        '''
        logger.debug('Factory')
        exporters = {
            'ApplicationInsights': ApplicationInsightsExporter
        }
        if exporter_type not in exporters:
            raise Exception('{0} is not a known exporter in MetricExporterFactory.'.format(exporter_type))
        return exporters[exporter_type]()
