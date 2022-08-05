from organizer.MetricOrganizer import MetricOrganizer
from organizer.MetricOrganizerFactory import MetricOrganizerFactory
from collector.MetricCollector import MetricCollector

from requests import Response, adapters, Session
from configparser import ConfigParser
import logging

MAX_RETRIES = 3

DCGM_METRICS = [
                'dcgm_gpu_utilization', 
                'dcgm_fp64_active', 
                'dcgm_memory_clock', 
                'dcgm_ecc_sbe_aggregate_total', 
                'dcgm_mem_copy_utilization', 
                'dcgm_ecc_sbe_volatile_total', 
                'dcgm_fp32_active', 
                'dcgm_sm_clock',
                'dcgm_ecc_dbe_volatile_total', 
                'dcgm_pcie_rx_bytes', 
                'dcgm_sm_occupancy', 
                'dcgm_dram_active', 
                'dcgm_power_usage', 
                'dcgm_ecc_dbe_aggregate_total', 
                'dcgm_gpu_temp', 
                'dcgm_sm_active', 
                'dcgm_memory_temp', 
                'dcgm_pcie_tx_bytes', 
                'dcgm_nvlink_rx_bytes', 
                'dcgm_tensor_active', 
                'dcgm_nvlink_tx_bytes', 
                'dcgm_total_energy_consumption', 
                'dcgm_fp16_active'
            ]
IB_METRICS = [
                'ib_port_rcv_data', 
                'ib_port_xmit_data'
            ]

CONFIG_FILE_NAME = 'config.ini'

logger = logging.getLogger(__name__)

class PrometheusMetricCollector(MetricCollector):
    
    def __init__(self):
        logger.debug('__init__')
        self._url = PrometheusMetricCollector.get_prometheus_url()
        self._current_results = {}

        self._session = Session()
        self._session.mount(self._url, adapters.HTTPAdapter(max_retries=MAX_RETRIES))
        if (not self.check_connection()):
            logger.error('Unable to check connection to the Prometheus port.')
            raise ConnectionError('Unable to check connection to the Prometheus port.')
    
    def collect_metrics(self):
        logger.debug('collect_metrics')
        dcgm_organizer = MetricOrganizerFactory.Factory("DCGM")
        self.collect_metrics_of_type(dcgm_organizer, DCGM_METRICS)

        ib_organizer = MetricOrganizerFactory.Factory('IB')
        self.collect_metrics_of_type(ib_organizer, IB_METRICS)

    def collect_metrics_of_type(self, organizer: MetricOrganizer, metric_list: list):
        '''Collects metrics of a specific given type
        
        Parameters
        ----------
        organizer : MetricOrganizer
            An instance of a subclass of MetricOrganizer that can organize metrics in the given list
        metric_list : list
            A list of metric names of the same type that can be organized through the previous parameter
        '''
        logger.debug('collect_metrics_of_type')
        for metric in metric_list:
            response = self.query_prometheus(metric)
            if (PrometheusMetricCollector.successful_response(response)):
                organized_metrics = organizer.organize_metric(response)
                for organized_metric in organized_metrics:
                    job_id, vm_instance, identifier, metric_queried, metric_value = organized_metric
                    self.log_to_current_results(job_id, vm_instance, identifier, metric_queried, metric_value)

    def query_prometheus(self, metric_name: str):
        '''Performs an http request to the specified Prometheus DB url in configuration file (i.e. config.ini) for the specific metric.
        
        Parameters
        ----------
        metric_name : str
            Name of the metric being queried for
        
        Returns
        -------
        response : requests.Response
            Http response associated with querying Prometheus for the metric
        '''
        logger.debug('query_prometheus')
        response = self._session.get('{0}/api/v1/query'.format(self._url), params= {'query': metric_name})
        if (not PrometheusMetricCollector.successful_response(response)):
            logger.warning('Request received status code {0} with content: {1} when querying for {2}.'.format(response.status_code, response.content, metric_name))
        return response
    
    def log_to_current_results(self, job_id: str, vm_instance: str, identifier: str, metric_queried: str, metric_value: str):
        '''Logs individual metric to private instance dictionary. 
        
        Parameters
        ----------
        job_id : str
            Job id of the job that generated this metric
        vm_instance : str
            Name of the VM instance that generated this metric
        identifier : str
            Name of the identifier that generated this metric (i.e. GPU index or IB Port)
        metric_queried : str
            Name of the metric queried for
        metric_value : str
            Value of the metric queried for as a string
        '''
        logger.debug('log_to_current_results')
        if self._current_results.get(job_id, None) == None:
            self._current_results[job_id] = {}
        if self._current_results[job_id].get(vm_instance, None) == None:
            self._current_results[job_id][vm_instance] = {}
        if self._current_results[job_id][vm_instance].get(identifier, None) == None:
            self._current_results[job_id][vm_instance][identifier] = {}
        self._current_results[job_id][vm_instance][identifier][metric_queried] = metric_value
    
    def check_connection(self):
        ''' Checks whether this can query the Prometheus Port.
        Returns
        -------
        bool
            Boolean representing whether the status code was 200
        '''
        logger.debug('check_connection')
        try: 
            response = self._session.get('{0}/'.format(self._url))
        except:
            return False
        return response.status_code == 200

    def get_url(self):
        logger.debug('get_url')
        return self._url
    
    def set_url(self, url: str):
        logger.debug('set_url')
        self._url = url
    
    def get_current_results(self):
        logger.debug('get_current_results')
        return self._current_results
    
    @staticmethod
    def get_prometheus_url():
        logger.debug('get_prometheus_url')
        config_parser = ConfigParser()
        config_parser.read(CONFIG_FILE_NAME)
        try:
            base_url = config_parser['prometheus']['base_url']
        except KeyError:
            raise KeyError('Missing Prometheus base url in {0}'.format(CONFIG_FILE_NAME))
        return base_url
    
    @staticmethod
    def successful_response(response: Response):
        logger.debug('successful_response')
        SUCCESSFUL_CODES = [200, 201, 202, 203, 204, 205, 206]
        return response.status_code in SUCCESSFUL_CODES




