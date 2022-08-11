import unittest

import sys
import os
import configparser

from helper import shell_process, file_util

sys.path.append('../src/azinsights')

from exporter.ApplicationInsightsExporter import ApplicationInsightsExporter
from exporter.MetricExporterFactory import MetricExporterFactory

PATH_TO_DATA = 'data/azinsights/exporter'
TEST_INSTR_KEY = 'INSIGHTS_INSTR_KEY'

class ExporterTestCase(unittest.TestCase):
    """Exporter unit test class"""

    def test_metric_exporter_factory_unknown(self):
        self.assertRaises(Exception, MetricExporterFactory.Factory, "Unknown")
    
    def test_metric_exporter_factory_insights(self):
        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        section = 'azure'
        option = 'instrumentation_key'
        value = os.environ[TEST_INSTR_KEY] #TODO: add this github secret to env vars
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        try:
            shell_process.deploy_moneo(24)
            exporter = MetricExporterFactory.Factory('ApplicationInsights')
            self.assertIsInstance(exporter, ApplicationInsightsExporter)
        except:
            raise Exception('Call to MetricExporterFactory caused an exception.')
        finally:
            os.remove(config_file_name)
    
    def test_application_insights_exporter_without_instrumentation_key(self):
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
            shell_process.deploy_moneo(24)
            self.assertRaises(Exception, ApplicationInsightsExporter)
        except:
            raise Exception('Call to MetricExporterFactory caused an exception.')
        finally:
            os.remove(config_file_name)

    def test_application_insights_exporter_export(self):
        collected_data = file_util.jsonToDict(PATH_TO_DATA + '/goodMetricsCollectedTwoVM.json')

        config_file_name = "config.ini"
        config = configparser.ConfigParser()
        section = 'prometheus'
        option = 'base_url'
        value = 'http://localhost:9090'
        config.add_section(section)
        config.set(section, option, value)
        section = 'azure'
        option = 'instrumentation_key'
        value = os.environ[TEST_INSTR_KEY]
        config.add_section(section)
        config.set(section, option, value)
        with open(config_file_name, 'w') as config_file:
            config.write(config_file)
        try:
            shell_process.deploy_moneo(24)
            exporter = ApplicationInsightsExporter()
            exporter.export(collected_data)
        except:
            raise Exception('Call to ApplicationInsightsExporter export caused an exception.')
        finally:
            os.remove(config_file_name)       

if __name__ == '__main__':
    unittest.main()
    
