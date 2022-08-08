# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import unittest
from unittest.mock import Mock

import requests
import sys

from helper import json_helper

sys.path.append('../src/azinsights')
from organizer.DCGMMetricOrganizer import DCGMMetricOrganizer
from organizer.IBMetricOrganizer import IBMetricOrganizer
from organizer.MetricOrganizerFactory import MetricOrganizerFactory

PATH_TO_DATA = 'data/azinsights/organizer'

class OrganizerTestCase(unittest.TestCase):
    """Organizer unit test class"""
    
    def getMockResponse(self, status_code: int, json_return_value: dict):
        resp = Mock(spec=requests.Response)
        resp.status_code = status_code
        resp.json.return_value = json_return_value
        return resp
    

    def test_metric_organizer_factory_dcgm(self):
        dcgm_organizer = MetricOrganizerFactory.Factory('DCGM')
        self.assertIsInstance(dcgm_organizer, DCGMMetricOrganizer)

    def test_metric_organizer_factory_ib(self):
        ib_organizer = MetricOrganizerFactory.Factory('IB')
        self.assertIsInstance(ib_organizer, IBMetricOrganizer)
    
    def test_metric_organizer_factory_unknown(self):
        self.assertRaises(Exception, MetricOrganizerFactory.Factory, "Unknown")

    def test_dcgm_organize_metric_single_vm(self):
        expected_organized_results = [
                                        ('42', 'nd96-1', '0', 'dcgm_gpu_temp', '36'), ('42', 'nd96-1', '1', 'dcgm_gpu_temp', '34'), 
                                        ('42', 'nd96-1', '2', 'dcgm_gpu_temp', '33'), ('42', 'nd96-1', '3', 'dcgm_gpu_temp', '35'), 
                                        ('42', 'nd96-1', '4', 'dcgm_gpu_temp', '36'), ('42', 'nd96-1', '5', 'dcgm_gpu_temp', '35'), 
                                        ('42', 'nd96-1', '6', 'dcgm_gpu_temp', '35'), ('42', 'nd96-1', '7', 'dcgm_gpu_temp', '36')
                                    ]
        dcgm_organizer = DCGMMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodDCGMResponse.json')
        response = self.getMockResponse(200, response_data)
        organized_results = dcgm_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)
    
    def test_dcgm_organize_metric_two_vm(self):
        expected_organized_results = [
                                        ('24', 'hpcpee58f000006', '0', 'dcgm_gpu_temp', '66'), ('24', 'hpcpee58f000004', '0', 'dcgm_gpu_temp', '33'),
                                        ('24', 'hpcpee58f000004', '1', 'dcgm_gpu_temp', '32'), ('24', 'hpcpee58f000006', '1', 'dcgm_gpu_temp', '63'), 
                                        ('24', 'hpcpee58f000006', '2', 'dcgm_gpu_temp', '63'), ('24', 'hpcpee58f000004', '2', 'dcgm_gpu_temp', '32'), 
                                        ('24', 'hpcpee58f000006', '3', 'dcgm_gpu_temp', '63'), ('24', 'hpcpee58f000004', '3', 'dcgm_gpu_temp', '32'), 
                                        ('24', 'hpcpee58f000006', '4', 'dcgm_gpu_temp', '64'), ('24', 'hpcpee58f000004', '4', 'dcgm_gpu_temp', '33'), 
                                        ('24', 'hpcpee58f000006', '5', 'dcgm_gpu_temp', '64'), ('24', 'hpcpee58f000004', '5', 'dcgm_gpu_temp', '32'), 
                                        ('24', 'hpcpee58f000006', '6', 'dcgm_gpu_temp', '61'), ('24', 'hpcpee58f000004', '6', 'dcgm_gpu_temp', '32'), 
                                        ('24', 'hpcpee58f000006', '7', 'dcgm_gpu_temp', '63'), ('24', 'hpcpee58f000004', '7', 'dcgm_gpu_temp', '33')
                                    ]
        dcgm_organizer = DCGMMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodDCGMResponseTwoVM.json')
        response = self.getMockResponse(200, response_data)
        organized_results = dcgm_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)

    def test_dcgm_organize_metric_with_ib(self):
        expected_organized_results = []
        dcgm_organizer = DCGMMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodIBResponseTwoVM.json')
        response = self.getMockResponse(200, response_data)
        organized_results = dcgm_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)
    
    def test_none_job_id_dcgm(self):
        expected_organized_results = [
                                        ('None', 'nd96-1', '0', 'dcgm_gpu_temp', '34'), ('None', 'nd96-1', '1', 'dcgm_gpu_temp', '33'), 
                                        ('None', 'nd96-1', '2', 'dcgm_gpu_temp', '32'), ('None', 'nd96-1', '3', 'dcgm_gpu_temp', '33'), 
                                        ('None', 'nd96-1', '4', 'dcgm_gpu_temp', '34'), ('None', 'nd96-1', '5', 'dcgm_gpu_temp', '34'), 
                                        ('None', 'nd96-1', '6', 'dcgm_gpu_temp', '34'), ('None', 'nd96-1', '7', 'dcgm_gpu_temp', '35')
                                    ]
        dcgm_organizer = DCGMMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/noneJobIdDCGMResponse.json')
        response = self.getMockResponse(200, response_data)
        organized_results = dcgm_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)
    
    def test_ib_organize_metric_single_vm(self):
        expected_organized_results = [
                                        ('42', 'nd96-1', 'mlx5_ib0:1', 'ib_port_xmit_data', '2880'), ('42', 'nd96-1', 'mlx5_ib1:1', 'ib_port_xmit_data', '180'), 
                                        ('42', 'nd96-1', 'mlx5_ib2:1', 'ib_port_xmit_data', '144'), ('42', 'nd96-1', 'mlx5_ib3:1', 'ib_port_xmit_data', '288'), 
                                        ('42', 'nd96-1', 'mlx5_ib4:1', 'ib_port_xmit_data', '0'), ('42', 'nd96-1', 'mlx5_ib5:1', 'ib_port_xmit_data', '0'),
                                        ('42', 'nd96-1', 'mlx5_ib6:1', 'ib_port_xmit_data', '151'), ('42', 'nd96-1', 'mlx5_ib7:1', 'ib_port_xmit_data', '160')
                                    ]
        ib_organizer = IBMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodIBResponse.json')
        response = self.getMockResponse(200, response_data)
        organized_results = ib_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)

    def test_ib_organize_metric_two_vm(self):
        expected_organized_results = [
                                        ('24', 'hpcpee58f000006', 'mlx5_ib0:1', 'ib_port_xmit_data', '144'), ('24', 'hpcpee58f000004', 'mlx5_ib0:1', 'ib_port_xmit_data', '0'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib1:1', 'ib_port_xmit_data', '288'), ('24', 'hpcpee58f000004', 'mlx5_ib1:1', 'ib_port_xmit_data', '0'),
                                        ('24', 'hpcpee58f000006', 'mlx5_ib2:1', 'ib_port_xmit_data', '0'), ('24', 'hpcpee58f000004', 'mlx5_ib2:1', 'ib_port_xmit_data', '144'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib3:1', 'ib_port_xmit_data', '144'), ('24', 'hpcpee58f000004', 'mlx5_ib3:1', 'ib_port_xmit_data', '0'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib4:1', 'ib_port_xmit_data', '288'), ('24', 'hpcpee58f000004', 'mlx5_ib4:1', 'ib_port_xmit_data', '151'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib5:1', 'ib_port_xmit_data', '0'), ('24', 'hpcpee58f000004', 'mlx5_ib5:1', 'ib_port_xmit_data', '0'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib6:1', 'ib_port_xmit_data', '0'), ('24', 'hpcpee58f000004', 'mlx5_ib6:1', 'ib_port_xmit_data', '0'), 
                                        ('24', 'hpcpee58f000006', 'mlx5_ib7:1', 'ib_port_xmit_data', '0'), ('24', 'hpcpee58f000004', 'mlx5_ib7:1', 'ib_port_xmit_data', '151')
                                    ]
        ib_organizer = IBMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodIBResponseTwoVM.json')
        response = self.getMockResponse(200, response_data)
        organized_results = ib_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)
    
    def test_ib_organize_metric_with_dcgm(self):
        expected_organized_results = []
        ib_organizer = IBMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/goodDCGMResponseTwoVM.json')
        response = self.getMockResponse(200, response_data)
        organized_results = ib_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)
    
    def test_none_job_id_ib(self):
        expected_organized_results = [
                                        ('None', 'nd96-1', 'mlx5_ib0:1', 'ib_port_rcv_data', '0'), ('None', 'nd96-1', 'mlx5_ib1:1', 'ib_port_rcv_data', '0'),
                                        ('None', 'nd96-1', 'mlx5_ib2:1', 'ib_port_rcv_data', '0'), ('None', 'nd96-1', 'mlx5_ib3:1', 'ib_port_rcv_data', '0'), 
                                        ('None', 'nd96-1', 'mlx5_ib4:1', 'ib_port_rcv_data', '0'), ('None', 'nd96-1', 'mlx5_ib5:1', 'ib_port_rcv_data', '0'), 
                                        ('None', 'nd96-1', 'mlx5_ib6:1', 'ib_port_rcv_data', '0'), ('None', 'nd96-1', 'mlx5_ib7:1', 'ib_port_rcv_data', '0')
                                    ]
        ib_organizer = IBMetricOrganizer()
        response_data = json_helper.jsonToDict(PATH_TO_DATA + '/noneJobIdIBResponse.json')
        response = self.getMockResponse(200, response_data)
        organized_results = ib_organizer.organize_metric(response)
        self.assertEqual(organized_results, expected_organized_results)


if __name__ == '__main__':
    unittest.main()
