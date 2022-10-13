import unittest
import shlex
from helper import shell_process
import os
import sys

p = os.path.abspath('../src/worker/exporters')
sys.path.insert(1, p)

from base_exporter import BaseExporter


"""Moneo Node Exporter test"""


class NodeExporterTestCase(unittest.TestCase):
    """Node Exporter unit test Class."""
    def test_base_class(self):
        """test that functions in this class aren't implemented"""
        fields = ['net_rx']
        config = {'listen_port': 8003}  # dummy
        exporter = BaseExporter(fields, config)
        test = False

        try:
            exporter.collect(fields[0])  # 'net_rx'=dummy
        except NotImplementedError:
            test = True
        assert (test)
        test = False

        try:
            exporter.cleanup()
        except NotImplementedError:
            test = True
        assert (test)

    def test_metrics(self):
        """Check that required metrics are being tracked"""
        path = os.path.dirname(__file__)
        if path:
            path = path + '/'

        metricData = [
            'net_rx',
            'net_tx',
            'cpu_util',
            'cpu_frequency',
            'mem_available',
            'mem_util'
        ]

        # Running node exporter for 5 seconds with debug log level. It will
        # out put the metrics monitored
        cmd = 'timeout 5  python3 ' + path + \
              '../src/worker/exporters/node_exporter.py --log_level DEBUG'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args, 20)
        for metric in metricData:
            assert (metric in result)


if __name__ == '__main__':
    unittest.main()
