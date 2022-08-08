import unittest

import sys
import os
import shlex
import configparser

sys.path.append('../src/azinsights')

from collector.MetricCollectorFactory import MetricCollectorFactory
from collector.PrometheusMetricCollector import PrometheusMetricCollector

from helper import shell_process

PATH_TO_DATA = 'data/azinsights/collector'

class CollectorTestCase(unittest.TestCase):
    """Collector unit test class"""

    
    
    def test_prometheus_metric_collector_without_config_ini(self):
        self.assertRaises(KeyError, PrometheusMetricCollector)
    
    def test_prometheus_metric_collector_without_resource(self):
        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        
        self.assertRaises(ConnectionError, PrometheusMetricCollector)

        os.remove(config_file_name)

    def test_prometheus_metric_collector_with_resource(self):
        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        
        try:
            shell_process.deploy_moneo(37)
            prometheus_collector = PrometheusMetricCollector()
        except:
            raise Exception('Call to PrometheusMetricCollector constructor caused an exception.')
        finally:
            os.remove(config_file_name)
    
    def test_metric_collector_factory_prometheus(self):
        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        
        try:
            shell_process.deploy_moneo(37)
            prometheus_collector = MetricCollectorFactory.Factory('Prometheus')
            self.assertIsInstance(prometheus_collector, PrometheusMetricCollector)
        except:
            raise Exception('Call to PrometheusMetricCollector constructor caused an exception.')
        finally:
            os.remove(config_file_name)
    
    def test_metric_collector_factory_unknown(self):
        self.assertRaises(Exception, MetricCollectorFactory.Factory, "Unknown")
        
    def test_prometheus_metric_collector_collect_metrics(self):
        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        
        try:
            shell_process.deploy_moneo(73)
            prometheus_collector = PrometheusMetricCollector()
            prometheus_collector.collect_metrics()
            current_results = prometheus_collector.get_current_results()
            self.assertGreaterEqual(len(current_results), 0)
        except:
            raise Exception('Call to PrometheusMetricCollector methods caused an exception.')
        finally:
            os.remove(config_file_name)

if __name__ == '__main__':
    unittest.main()
        
        
    
    