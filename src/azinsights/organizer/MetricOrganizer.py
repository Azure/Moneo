from requests import Response
import logging

logger = logging.getLogger(__name__)

class MetricOrganizer:
    def __init__():
        pass

    def organize_metric(self):
        '''Organizes a metric.'''
        raise NotImplementedError('Must implement this method')

    def organize_results(self):
        '''Organizes results.'''
        pass

    def get_result_list_from_json(self, json: dict):
        '''Gets the result list from json'''
        return json['data']['result']

    def extract_metric_info(self):
        '''Extracts metric information.'''
        pass

    @staticmethod
    def successful_response(response: Response):
        logger.debug('successful_response')
        SUCCESSFUL_CODES = [200, 201, 202, 203, 204, 205, 206]
        return response.status_code in SUCCESSFUL_CODES

