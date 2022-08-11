from exporter.MetricExporter import MetricExporter

from configparser import ConfigParser
import json
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import logging

stats = stats_module.stats
JOB_ID_TAGKEY = tag_map_module.TagKey('Job Id')
VM_INSTANCE_TAGKEY = tag_map_module.TagKey('VM Instance')
GPU_IDENTIFIER_TAGKEY = tag_map_module.TagKey('GPU')
IB_PORT_IDENTIFIER_TAGKEY = tag_map_module.TagKey('IB Port')

CONFIG_FILE_NAME = 'config.ini'

logger = logging.getLogger(__name__)

class ApplicationInsightsExporter(MetricExporter):
    '''Class meant to receive metrics from a collector and send them to an Azure Application Insights resource.'''

    def __init__(self):
        logger.debug('__init__')
        self._instrumentation_key = ApplicationInsightsExporter.get_azure_instrumentation_key()
        self._view_manager = stats.view_manager
        self._stats_recorder = stats.stats_recorder
        try:
            self._metrics_exporter = metrics_exporter.new_metrics_exporter(connection_string=self._instrumentation_key)
        except ValueError:
            raise ValueError('Invalid Instrumentation Key in the {0} file.'.format(CONFIG_FILE_NAME))
        self._metric_measures = self.init_measures_and_views()
        self._context = tag_map_module.TagMap()
        self._measurement_map = stats.stats_recorder.new_measurement_map()
        
        self._view_manager.register_exporter(self._metrics_exporter)

    def export(self, data: dict):
        logger.debug('export')
        if (data == None or data == {}):
            logger.warning('Data to be exported was {0}. Skipping export step.'.format(data))
        else:
            for job_id in data:
                vm_instance_data = data[job_id]
                self.add_job_id_context(job_id)
                for vm_instance in vm_instance_data:
                    identifier_data = vm_instance_data[vm_instance]
                    self.add_vm_instance_context(vm_instance)
                    for identifier in identifier_data:
                        metric_data = identifier_data[identifier]
                        self.add_identifier_context(identifier)
                        for metric in metric_data:
                            value = float(metric_data[metric])
                            self.record_float_metric(value, metric)
                        self.push_metrics()
    
    def push_metrics(self):
        '''Pushes metrics to Azure Insights considering the current context of VM instance and identifier.'''
        logger.debug('push_metrics')
        self._measurement_map.record(self._context)
        self._measurement_map = stats.stats_recorder.new_measurement_map()

    def record_float_metric(self, value: float, metric_name: str):
        '''Records an individual float metric to be pushed.
        
        Parameters
        ----------
        value : float
            Metric value to be recorded
        metric_name : str 
            Metric name associated with the value
        '''
        logger.debug('record_float_metric')
        measure = self._metric_measures[metric_name]
        self._measurement_map.measure_float_put(measure, value)
    
    def add_job_id_context(self, value: str):
        '''Adds Job Id context to metrics about to be pushed
        
        Parameters
        ----------
        value : str
            Job Id
        '''
        logger.debug('add_job_id_context')
        if (self._context.tag_key_exists(JOB_ID_TAGKEY)):
            self._context.update(JOB_ID_TAGKEY, value)
        else: 
            self._context.insert(JOB_ID_TAGKEY, value)


    def add_identifier_context(self, value: str):
        '''Adds context to metrics about to be pushed (i.e. GPU index or IB port)
        
        Parameters
        ----------
        value : str
            GPU index as a string or IB port name
        '''
        logger.debug('add_identifier_context')
        if (value.isdecimal()): #GPU ID
            self.add_gpu_context(value)
            self.remove_ib_port_context()
        else: #IB Port
            self.add_ib_port_context(value)
            self.remove_gpu_context()

    def remove_ib_port_context(self):
        '''Removes IB Port context whenever GPU index context is used'''
        logger.debug('remove_ib_port_context')
        if (self._context.tag_key_exists(IB_PORT_IDENTIFIER_TAGKEY)):
            self._context.delete(IB_PORT_IDENTIFIER_TAGKEY)
    
    def remove_gpu_context(self):
        '''Removes GPU index context whenever IB port context is used'''
        logger.debug('remove_gpu_context')
        if (self._context.tag_key_exists(GPU_IDENTIFIER_TAGKEY)):
            self._context.delete(GPU_IDENTIFIER_TAGKEY)

    def add_ib_port_context(self, value: str):
        '''Adds IB port context to metrics about to be pushed
        
        Parameters
        ----------
        value : str
            IB port name
        '''
        logger.debug('add_ib_port_context')
        if (self._context.tag_key_exists(IB_PORT_IDENTIFIER_TAGKEY)):
            self._context.update(IB_PORT_IDENTIFIER_TAGKEY, value)
        else: 
            self._context.insert(IB_PORT_IDENTIFIER_TAGKEY, value)
    
    def add_gpu_context(self, value: str):
        '''Adds GPU index context to metrics about to be pushed
        
        Parameters
        ----------
        value : str
            GPU index as a string
        '''
        logger.debug('add_gpu_context')
        if (self._context.tag_key_exists(GPU_IDENTIFIER_TAGKEY)):
            self._context.update(GPU_IDENTIFIER_TAGKEY, value)
        else: 
            self._context.insert(GPU_IDENTIFIER_TAGKEY, value)
    
    def add_vm_instance_context(self, value: str):
        '''Adds VM instance context to metrics about to be pushed
        
        Parameters
        ----------
        value : str
            VM instance name
        '''
        logger.debug('add_vm_instance_context')
        if (self._context.tag_key_exists(VM_INSTANCE_TAGKEY)):
            self._context.update(VM_INSTANCE_TAGKEY, value)
        else: 
            self._context.insert(VM_INSTANCE_TAGKEY, value)

    def init_measures_and_views(self, path_to_metric_info: str = 'metric_info.json'):
        ''' Initiates OpenCensus measures and views for them to be exported.
        
        Parameters
        ----------
        path_to_metric_info : str
            Path to metric_info.json with information about metrics
        
        Returns
        -------
        metric_measures : dict
            Dictionary with keys as the metric names and measures as their values
        '''
        logger.debug('init_measures_and_views')
        with open(path_to_metric_info) as metric_info_file:
            metric_info = json.load(metric_info_file)
        metric_measures = {}
        for metric in metric_info:
            description = metric_info[metric]['description']
            unit = metric_info[metric]['unit']
            measure = measure_module.MeasureFloat(metric, description, unit)
            metric_type = metric_info[metric]['type']
            metric_measures[metric] = measure
            self.register_view(metric_type, metric, description, measure)
        return metric_measures
    
    def register_view(self, metric_type: str, name: str, description: str, measure: measure_module.BaseMeasure):
        ''' Registers OpenCensus views for an individual metric
        
        Parameters
        ----------
        metric_type : str
            Type of metric, either dcgm or ib
        name : str
            Name of the metric
        description : str
            Description of the metric
        measure : measure_module.BaseMeasure
            OpenCensus measure for this view
        '''
        logger.debug('register_view')
        if (metric_type == 'dcgm'):
            self.register_dcgm_view(name, description, measure)
        elif (metric_type == 'ib'):
            self.register_ib_view(name, description, measure)
        else:
            logger.warning('View of type {0} is unknown and was not registered.'.format(metric_type))
    
    def register_dcgm_view(self, name: str, description: str, measure: measure_module.BaseMeasure):
        ''' Registers OpenCensus views for a dcgm metric
        
        Parameters
        ----------
        name : str
            Name of the metric
        description : str
            Description of the metric
        measure : measure_module.BaseMeasure
            OpenCensus measure for this view
        '''
        logger.debug('register_dcgm_view')
        view = view_module.View(name, description, columns = [JOB_ID_TAGKEY, VM_INSTANCE_TAGKEY, GPU_IDENTIFIER_TAGKEY], measure= measure, aggregation= aggregation_module.LastValueAggregation())
        self._view_manager.register_view(view)
    
    def register_ib_view(self, name: str, description: str, measure: measure_module.BaseMeasure):
        ''' Registers OpenCensus views for a ib metric
        
        Parameters
        ----------
        name : str
            Name of the metric
        description : str
            Description of the metric
        measure : measure_module.BaseMeasure
            OpenCensus measure for this view
        '''
        logger.debug('register_ib_view')
        view = view_module.View(name, description, columns = [JOB_ID_TAGKEY, VM_INSTANCE_TAGKEY, IB_PORT_IDENTIFIER_TAGKEY], measure= measure, aggregation= aggregation_module.LastValueAggregation())
        self._view_manager.register_view(view)
    
    def get_instrumentation_key(self):
        logger.debug('get_instrumentation_key')
        return self._instrumentation_key
    
    def set_instrumentation_key(self, instrumentation_key: str):
        logger.debug('set_instrumentation_key')
        self._instrumentation_key = instrumentation_key
    
    @staticmethod
    def get_azure_instrumentation_key():
        logger.debug('get_azure_instrumentation_key')
        config_parser = ConfigParser()
        config_parser.read(CONFIG_FILE_NAME)
        return config_parser['azure']['instrumentation_key']
        