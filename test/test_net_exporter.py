import unittest
import shlex
from helper import shell_process
from helper import file_util


"""Moneo Net Exporter test"""

class NetExporterTestCase(unittest.TestCase):
    """Net Exporter unit test Class."""
    def test_IB_metrics(self):
        """Check that required metrics are being tracked"""
        metricData= file_util.load_data('data/ib_metric.txt')
        metricData = metricData.split("\n")
        #running net exporter for 0.2 seconds with debug log level. It will out put the metrics monitored
        cmd='timeout 0.2 python3 ../src/worker/exporters/net_exporter.py --log_level DEBUG'
        args = shlex.split(cmd)
        result = shell_process.shell_cmd(args,15)
        for metric in metricData:
            assert(metric in result)
        
    # def test_front_net_metrics(self):
        # print("Network Front end metric exporting has not been implemented")
        # assert(False)
        
        
if __name__ == '__main__':
    unittest.main()
