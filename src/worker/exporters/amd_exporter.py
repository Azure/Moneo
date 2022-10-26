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
    '/opt/rocm/rdc/python_binding',
])

from rsmiBindings import rocmsmi, rsmi_status_t
from RdcReader import RdcReader
from rdc_bootstrap import *  # noqa: F403

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
    # CU
    # rdc_field_t.RDC_FI_PROF_SM_ACTIVE,
    # rdc_field_t.RDC_FI_PROF_SM_OCCUPANCY,
    # rdc_field_t.RDC_FI_PROF_PIPE_TENSOR_ACTIVE,
    # rdc_field_t.RDC_FI_PROF_PIPE_FP64_ACTIVE,
    # rdc_field_t.RDC_FI_PROF_PIPE_FP32_ACTIVE,
    # rdc_field_t.RDC_FI_PROF_PIPE_FP16_ACTIVE,
    # Memory
    # rdc_field_t.RDC_FI_PROF_DRAM_ACTIVE,
    # xGMI
    # rdc_field_t.RDC_FI_PROF_NVLINK_TX_BYTES,
    # rdc_field_t.RDC_FI_PROF_NVLINK_RX_BYTES,
    # PCIe
    rdc_field_t.RDC_FI_PCIE_TX,
    rdc_field_t.RDC_FI_PCIE_RX,
]


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
        self.guages = {}
        for field_id in self.field_ids:
            field_name = self.rdc_util.field_id_string(field_id).lower()
            self.guages[field_id] = prometheus_client.Gauge(
                'rdc_{}'.format(field_name),
                'rdc_{}'.format(field_name),
                ['gpu_id', 'gpu_uuid'],
            )

    def handle_field(self, gpu_id, value):
        if value.field_id.value in self.guages:
            self.guages[value.field_id.value].labels(
                gpu_id,
                rdc_config['device_uuid'][gpu_id],
            ).set(value.value.l_int)
            logging.debug(
                'Sent GPU %d %s : %s=%s', gpu_id,
                rdc_config['device_uuid'][gpu_id],
                self.rdc_util.field_id_string(value.field_id).lower(),
                str(value.value.l_int))

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
