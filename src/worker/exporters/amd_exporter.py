import os
import sys
import time
import signal
import ctypes
import logging

import prometheus_client

sys.path.extend([
    '/opt/rocm/libexec/rocm_smi',   # ROCm >=5.2
    '/opt/rocm/rocm_smi/bindings',  # ROCm <5.2
    '/opt/rdc/python_binding',
])

from rsmiBindings import *
from RdcReader import RdcReader
from rdc_bootstrap import *  # noqa: F403

PRINT_JSON = True
rocmsmi = initRsmiBindings(silent=PRINT_JSON)

RDC_FIELDS = [
    # PID
    # rdc_field_t.RDC_FI_DEV_COMPUTE_PIDS,
    # Clock
    rdc_field_t.RDC_FI_GPU_CLOCK,
    rdc_field_t.RDC_FI_MEM_CLOCK,
    # Temperature
    rdc_field_t.RDC_FI_GPU_TEMP,
    rdc_field_t.RDC_FI_MEMORY_TEMP,
    # Power
    rdc_field_t.RDC_FI_POWER_USAGE,
    # rdc_field_t.RDC_FI_DEV_TOTAL_ENERGY_CONSUMPTION,
    # Utilization
    rdc_field_t.RDC_FI_GPU_UTIL,
    rdc_field_t.RDC_FI_GPU_MEMORY_USAGE,
    rdc_field_t.RDC_FI_GPU_MEMORY_TOTAL,
    # ECC
    # rdc_field_t.RDC_FI_DEV_ECC_SBE_VOL_TOTAL,
    # rdc_field_t.RDC_FI_DEV_ECC_DBE_VOL_TOTAL,
    rdc_field_t.RDC_FI_ECC_CORRECT_TOTAL,
    rdc_field_t.RDC_FI_ECC_UNCORRECT_TOTAL,

    # PCIe
    rdc_field_t.RDC_FI_PCIE_BANDWIDTH,

    # xGMI
    rdc_field_t.RDC_FI_XGMI_0_READ_KB,
    rdc_field_t.RDC_FI_XGMI_1_READ_KB,
    rdc_field_t.RDC_FI_XGMI_2_READ_KB,
    rdc_field_t.RDC_FI_XGMI_3_READ_KB,
    rdc_field_t.RDC_FI_XGMI_4_READ_KB,
    rdc_field_t.RDC_FI_XGMI_5_READ_KB,
    rdc_field_t.RDC_FI_XGMI_6_READ_KB,
    rdc_field_t.RDC_FI_XGMI_7_READ_KB,
    rdc_field_t.RDC_FI_XGMI_0_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_1_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_2_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_3_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_4_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_5_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_6_WRITE_KB,
    rdc_field_t.RDC_FI_XGMI_7_WRITE_KB,
]

RDC_FIELDS_DESCRIPTION = {
    # PID
    # rdc_field_t.RDC_FI_DEV_COMPUTE_PIDS,
    # Clock
    rdc_field_t.RDC_FI_GPU_CLOCK:
    'The current clock for the GPU',
    rdc_field_t.RDC_FI_MEM_CLOCK:
    'Clock for the memory',
    # Temperature
    rdc_field_t.RDC_FI_GPU_TEMP:
    'Current temperature for the device',
    rdc_field_t.RDC_FI_MEMORY_TEMP:
    'Memory temperature for the device',
    # Power
    rdc_field_t.RDC_FI_POWER_USAGE:
    'Power usage for the device',

    # Utilization
    rdc_field_t.RDC_FI_GPU_UTIL:
    'GPU Utilization',
    rdc_field_t.RDC_FI_GPU_MEMORY_USAGE:
    'Memory usage of the GPU instance',
    rdc_field_t.RDC_FI_GPU_MEMORY_TOTAL:
    'Total memory of the GPU instance',
    # ECC
    rdc_field_t.RDC_FI_ECC_CORRECT_TOTAL:
    'Accumulated correctable ECC errors',
    rdc_field_t.RDC_FI_ECC_UNCORRECT_TOTAL:
    'Accumulated uncorrectable ECC errors',

    # PCIe
    rdc_field_t.RDC_FI_PCIE_BANDWIDTH:
    'PCIe bandwidth in GB/sec',

    # xGMI
    rdc_field_t.RDC_FI_XGMI_0_READ_KB:
    'XGMI_0 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_1_READ_KB:
    'XGMI_1 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_2_READ_KB:
    'XGMI_2 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_3_READ_KB:
    'XGMI_3 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_4_READ_KB:
    'XGMI_4 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_5_READ_KB:
    'XGMI_5 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_6_READ_KB:
    'XGMI_6 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_7_READ_KB:
    'XGMI_7 accumulated data read size (KB)',
    rdc_field_t.RDC_FI_XGMI_0_WRITE_KB:
    'XGMI_0 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_1_WRITE_KB:
    'XGMI_1 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_2_WRITE_KB:
    'XGMI_2 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_3_WRITE_KB:
    'XGMI_3 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_4_WRITE_KB:
    'XGMI_4 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_5_WRITE_KB:
    'XGMI_5 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_6_WRITE_KB:
    'XGMI_6 accumulated data write size (KB)',
    rdc_field_t.RDC_FI_XGMI_7_WRITE_KB:
    'XGMI_7 accumulated data write size (KB)',
}


class RdcExporter(RdcReader):
    def __init__(self):
        RdcReader.__init__(
            self,
            ip_port=rdc_config['rdc_ip_port'],
            field_ids=RDC_FIELDS,
            update_freq=100000,
            max_keep_age=1800.0,
            max_keep_samples=1200,
            gpu_indexes=None,
            field_group_name='rdc_exporter_{}'.format(os.getpid()),
        )
        self.init_connection()
        self.init_gauges()

    def init_connection(self):
        prometheus_client.start_http_server(rdc_config['listen_port'])
        logging.info('Started prometheus client')

        field_name_list = []
        for field_id in self.field_ids:
            field_name_list.append(
                self.rdc_util.field_id_string(field_id).lower())
        logging.info('Publishing fields: {}'.format(','.join(field_name_list)))

    def init_gauges(self):
        self.gauges = {}
        for field_id in self.field_ids:
            field_name = self.rdc_util.field_id_string(field_id).lower()
            self.gauges[field_id] = prometheus_client.Gauge(
                'rdc_{}'.format(field_name),
                RDC_FIELDS_DESCRIPTION[field_id],
                ['gpu_id', 'gpu_uuid'],
            )
        self.gauges['dummy_field'] = prometheus_client.Gauge('dummy_field', 'dummy_field', ['gpu_id', 'gpu_uuid'],)

    def handle_field(self, gpu_id, value):
        if value.field_id.value in self.gauges:
            self.gauges[value.field_id.value].labels(
                gpu_id,
                rdc_config['device_uuid'][gpu_id],
            ).set(value.value.l_int)
            logging.debug(
                'Sent GPU %d %s : %s=%s', gpu_id,
                rdc_config['device_uuid'][gpu_id],
                self.rdc_util.field_id_string(value.field_id).lower(),
                str(value.value.l_int))
        self.gauges['dummy_field'].labels(
            gpu_id,
            rdc_config['device_uuid'][gpu_id],
        ).set(1)

    def loop(self):
        try:
            while True:
                self.process()
                time.sleep(0.1)

                if rdc_config['exit'] is True:
                    logging.info('Received exit signal, shutting down ...')
                    break
        except KeyboardInterrupt:
            pass


def init_config():
    global rdc_config
    rdc_config = {
        'exit': False,
        'listen_port': 8000,
        'publish_interval': 1,
        'rdc_embedded': False,
        'rdc_ip_port': 'localhost:50051',
        'rdc_unauth': True,
        'field_ids': RDC_FIELDS,
        'device_uuid': [],
    }


def init_rocm_smi():
    rocmsmi.rsmi_init(0)
    devNum = ctypes.c_uint32(0)
    rocmsmi.rsmi_num_monitor_devices(byref(devNum))
    for dev in range(devNum.value):
        dev_uuid = ctypes.c_uint64()
        ret = rocmsmi.rsmi_dev_unique_id_get(dev, byref(dev_uuid))
        if ret == rsmi_status_t.RSMI_STATUS_SUCCESS and str(hex(
                dev_uuid.value)):
            rdc_config['device_uuid'].append(str(hex(dev_uuid.value)))
        else:
            rdc_config['device_uuid'].append('N/A')


def init_signal_handler():
    def exit_handler(signalnum, frame):
        rdc_config['exit'] = True

    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)


def main():
    logging.basicConfig(level=logging.INFO)
    init_config()
    init_rocm_smi()
    init_signal_handler()

    exporter = RdcExporter()
    exporter.loop()


if __name__ == '__main__':
    main()
