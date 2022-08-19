import unittest
import shlex
from helper import shell_process
from helper import file_util
import os

"""Moneo Nvidia Exporter test"""

class NvidiaExporterTestCase(unittest.TestCase):
    """Nvidia Exporter unit test Class."""
    def test_metrics(self):
        """Check that required metrics are being tracked"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'
        metricData= file_util.load_data(path+'data/nv_metric.txt')
        metricData = metricData.split("\n")
        #running nvidia exporter for 5 seconds with debug log level. It will out put the metrics monitored
        cmd='timeout 5  python2 ' + path + '../src/worker/exporters/nvidia_exporter.py --log-level DEBUG'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args, 20)
        for metric in metricData:
            assert(metric in result)


    def test_metrics_prof(self):
        """Check that required metrics are being tracked"""
        path=os.path.dirname(__file__)
        if path:
            path=path + '/'
        metricData= file_util.load_data(path+'data/nv_metric2.txt')
        metricData = metricData.split("\n")
        #running nvidia exporter for 5 seconds with debug log level. It will out put the metrics monitored
        cmd='timeout 5  python2 ' + path + '../src/worker/exporters/nvidia_exporter.py -m --log-level DEBUG'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,20)
        for metric in metricData:
            assert(metric in result)     


if __name__ == '__main__':
    unittest.main()
