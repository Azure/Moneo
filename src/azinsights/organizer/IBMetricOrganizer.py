from organizer.MetricOrganizer import MetricOrganizer

from requests import Response
import logging

logger = logging.getLogger(__name__)

class IBMetricOrganizer(MetricOrganizer):
    '''Metric organizer for ib metrics.'''
    def __init__(self):
        logger.debug('__init__')
        pass

    def organize_metric(self, query_response: Response):
        logger.debug('organize_metric')
        results = self.get_result_list_from_json(query_response.json())
        organized_results = self.organize_results(results)
        return organized_results
    
    def organize_results(self, query_results: dict):
        logger.debug('organize_results')
        organized_results = []
        for result in query_results:
            try:
                metric_info = self.extract_metric_info(result)
                organized_results.append(metric_info)
            except KeyError:
                logger.warning('{0} did not have expected format to properly extract metric information.'.format(result))
        return organized_results
    
    def extract_metric_info(self, query_result: dict):
        logger.debug('extract_metric_info')
        metric = query_result['metric']
        job_id = '-999'
        job_id = job_id if (job_id != '-999') else None
        vm_instance = metric['instance']
        ib_port = metric['ib_port']
        metric_queried = metric['__name__']
        metric_value = query_result['value'][1]
        return job_id, vm_instance, ib_port, metric_queried, metric_value