from collector.MetricCollectorFactory import MetricCollectorFactory
from exporter.MetricExporterFactory import MetricExporterFactory

from time import sleep
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SAMPLE_RATE = 5 # in seconds

def main():
    logger.info('Starting up azinsights_main.')
    metric_collector = MetricCollectorFactory.Factory('Prometheus')
    metric_exporter = MetricExporterFactory.Factory('ApplicationInsights')
    try: 
        while True:
            logger.info('Collecting metrics...')
            metric_collector.collect_metrics()
            logger.info('Metrics collected.')
            logger.debug(metric_collector.get_current_results())
            logger.info('Exporting metrics...')
            metric_exporter.export(metric_collector.get_current_results())
            logger.info('Metrics exported.')
            logger.info('Waiting {0} seconds...'.format(SAMPLE_RATE))
            sleep(SAMPLE_RATE)
    except KeyboardInterrupt:
        logger.info('Shutting down azinsights_main.')


if __name__ == '__main__':
    main()
