import os
import sys
import time
import signal
import logging

import prometheus_client
sys.path.append('/usr/local/dcgm/bindings/python3')
#sys.path.append('/usr/local/dcgm/bindings')
import dcgm_fields
from DcgmReader import DcgmReader
from common import dcgm_client_cli_parser


DCGM_PROF_FIELDS = [
    dcgm_fields.DCGM_FI_PROF_PIPE_TENSOR_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_PIPE_FP64_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_PIPE_FP32_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_PIPE_FP16_ACTIVE,
]

DCGM_FIELDS = [
    # PID
    # dcgm_fields.DCGM_FI_DEV_COMPUTE_PIDS,
    # Clock
    dcgm_fields.DCGM_FI_DEV_SM_CLOCK,
    dcgm_fields.DCGM_FI_DEV_MEM_CLOCK,
    # Temperature
    dcgm_fields.DCGM_FI_DEV_GPU_TEMP,
    dcgm_fields.DCGM_FI_DEV_MEMORY_TEMP,
    # Power
    dcgm_fields.DCGM_FI_DEV_POWER_USAGE,
    dcgm_fields.DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION,
    # Utilization
    dcgm_fields.DCGM_FI_DEV_GPU_UTIL,
    dcgm_fields.DCGM_FI_DEV_MEM_COPY_UTIL,
    # ECC
    dcgm_fields.DCGM_FI_DEV_ECC_SBE_VOL_TOTAL,
    dcgm_fields.DCGM_FI_DEV_ECC_DBE_VOL_TOTAL,
    dcgm_fields.DCGM_FI_DEV_ECC_SBE_AGG_TOTAL,
    dcgm_fields.DCGM_FI_DEV_ECC_DBE_AGG_TOTAL,
    # SM
    dcgm_fields.DCGM_FI_PROF_SM_ACTIVE,
    dcgm_fields.DCGM_FI_PROF_SM_OCCUPANCY,
    # Memory
    dcgm_fields.DCGM_FI_PROF_DRAM_ACTIVE,
    # NVLink
    dcgm_fields.DCGM_FI_PROF_NVLINK_TX_BYTES,
    dcgm_fields.DCGM_FI_PROF_NVLINK_RX_BYTES,
    # PCIe
    dcgm_fields.DCGM_FI_PROF_PCIE_TX_BYTES,
    dcgm_fields.DCGM_FI_PROF_PCIE_RX_BYTES,
    #throttling and violations
    dcgm_fields.DCGM_FI_DEV_CLOCK_THROTTLE_REASONS,
    dcgm_fields.DCGM_FI_DEV_POWER_VIOLATION,
    dcgm_fields.DCGM_FI_DEV_THERMAL_VIOLATION,
]

DCGM_FIELDS_DESCRIPTION = {
    # PID
    # dcgm_fields.DCGM_FI_DEV_COMPUTE_PIDS,
    # Clock
    dcgm_fields.DCGM_FI_DEV_SM_CLOCK:
    'SM clock frequency (in MHz)',
    dcgm_fields.DCGM_FI_DEV_MEM_CLOCK:
    'Memory clock frequency (in MHz)',
    # Temperature
    dcgm_fields.DCGM_FI_DEV_GPU_TEMP:
    'GPU temperature (in C)',
    dcgm_fields.DCGM_FI_DEV_MEMORY_TEMP:
    'Memory temperature (in C)',
    # Power
    dcgm_fields.DCGM_FI_DEV_POWER_USAGE:
    'Power usage (in W)',
    dcgm_fields.DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION:
    'Total energy consumption since boot (in mJ)',
    # Utilization
    dcgm_fields.DCGM_FI_DEV_GPU_UTIL:
    'GPU utilization (in %)',
    dcgm_fields.DCGM_FI_DEV_MEM_COPY_UTIL:
    'Memory utilization (in %)',
    # ECC
    dcgm_fields.DCGM_FI_DEV_ECC_SBE_VOL_TOTAL:
    'Total number of single-bit volatile ECC errors',
    dcgm_fields.DCGM_FI_DEV_ECC_DBE_VOL_TOTAL:
    'Total number of double-bit volatile ECC errors',
    dcgm_fields.DCGM_FI_DEV_ECC_SBE_AGG_TOTAL:
    'Total number of single-bit persistent ECC errors',
    dcgm_fields.DCGM_FI_DEV_ECC_DBE_AGG_TOTAL:
    'Total number of double-bit persistent ECC errors',
    # SM
    dcgm_fields.DCGM_FI_PROF_SM_ACTIVE:
    'The fraction of time at least one warp was active on a multiprocessor, averaged over all multiprocessors',
    dcgm_fields.DCGM_FI_PROF_SM_OCCUPANCY:
    'The fraction of resident warps on a multiprocessor, relative to the maximum number of concurrent warps supported on a multiprocessor',
    dcgm_fields.DCGM_FI_PROF_PIPE_TENSOR_ACTIVE:
    'The fraction of cycles the tensor (HMMA / IMMA) pipe was active',
    dcgm_fields.DCGM_FI_PROF_PIPE_FP64_ACTIVE:
    'The fraction of cycles the FP64 (double precision) pipe was active',
    dcgm_fields.DCGM_FI_PROF_PIPE_FP32_ACTIVE:
    'The fraction of cycles the FMA (FP32 (single precision), and integer) pipe was active',
    dcgm_fields.DCGM_FI_PROF_PIPE_FP16_ACTIVE:
    'The fraction of cycles the FP16 (half precision) pipe was active',
    # Memory
    dcgm_fields.DCGM_FI_PROF_DRAM_ACTIVE:
    'The fraction of cycles where data was sent to or received from device memory',
    # NVLink
    dcgm_fields.DCGM_FI_PROF_NVLINK_TX_BYTES:
    'The rate of data transmitted over NVLink, not including protocol headers, in bytes per second',
    dcgm_fields.DCGM_FI_PROF_NVLINK_RX_BYTES:
    'The rate of data received over NVLink, not including protocol headers, in bytes per second',
    # PCIe
    dcgm_fields.DCGM_FI_PROF_PCIE_TX_BYTES:
    'The rate of data transmitted over the PCIe bus, including both protocol headers and data payloads, in bytes per second',
    dcgm_fields.DCGM_FI_PROF_PCIE_RX_BYTES:
    'The rate of data received over the PCIe bus, including both protocol headers and data payloads, in bytes per second',
    dcgm_fields.DCGM_FI_DEV_CLOCK_THROTTLE_REASONS: 
    'Current clock throttle reasons (bitmask of DCGM_CLOCKS_THROTTLE_REASON_*)',
    dcgm_fields.DCGM_FI_DEV_POWER_VIOLATION:     
    'Power Violation time in usec',
    dcgm_fields.DCGM_FI_DEV_THERMAL_VIOLATION: 
    'Thermal Violation time in usec',
}

class DcgmExporter(DcgmReader):
    def __init__(self):
        DcgmReader.__init__(
            self,
            fieldIds=dcgm_config['publishFieldIds'],
            ignoreList=dcgm_config['ignoreList'],
            # updateFrequency=(dcgm_config['prometheusPublishInterval'] *
            #                  1000000) / 2,
            updateFrequency=100000,
            maxKeepAge=1800.0,
            fieldGroupName='dcgm_exporter_{}'.format(os.getpid()),
            hostname=dcgm_config['dcgmHostName'],
        )
        self.InitConnection()
        self.InitGauges()
        signal.signal(signal.SIGUSR1,self.jobID_update_flag)

    def InitConnection(self):
        self.Reconnect()

        prometheus_client.start_http_server(dcgm_config['prometheusPort'])
        logging.info('Started prometheus client')

        fieldTagList = []

        for fieldId in self.m_publishFields[self.m_updateFreq]:
            if fieldId in self.m_dcgmIgnoreFields:
                continue
            fieldTagList.append(self.m_fieldIdToInfo[fieldId].tag)
        logging.info('Publishing fields: {}'.format(','.join(fieldTagList)))

    def InitGauges(self):
        self.m_gauges = {}
        for fieldId in self.m_publishFields[self.m_updateFreq]:
            if fieldId in self.m_dcgmIgnoreFields:
                continue

            self.m_gauges[fieldId] = prometheus_client.Gauge(
                'dcgm_{}'.format(self.m_fieldIdToInfo[fieldId].tag),
                DCGM_FIELDS_DESCRIPTION[fieldId],
                [
                    'gpu_id',
                    'gpu_uuid' if dcgm_config['sendUuid'] else 'gpu_bus_id',
                    'job_id'
                ],
            )

    def CustomDataHandler(self, fvs):
        for gpuId in fvs.keys():
            gpuUuid = self.m_gpuIdToUUId[gpuId]
            gpuBusId = self.m_gpuIdToBusId[gpuId]
            gpuUniqueId = gpuUuid if dcgm_config['sendUuid'] else gpuBusId

            gpu_line = [str(gpuId), gpuUniqueId]
            for fieldId in self.m_publishFields[self.m_updateFreq]:
                if fieldId in self.m_dcgmIgnoreFields:
                    continue

                val = fvs[gpuId][fieldId][-1]
                if val.isBlank:
                    continue

                self.m_gauges[fieldId].labels(
                    gpuId,
                    gpuUniqueId,
                    dcgm_config['jobId']
                ).set(val.value)
                gpu_line.append(str(val.value))

                logging.debug('Sent GPU %d %s : %s=%s', gpuId,
                              gpuUniqueId, self.m_fieldIdToInfo[fieldId].tag,
                              str(val.value))
            logging.debug(','.join(gpu_line))
    
    def jobID_update_flag(self, signum, stack):
        '''Sets job update flag when user defined signal comes in'''
        global job_update
        job_update=True
            
    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        global job_update
        job_update=False
        fvs = self.m_dcgmGroup.samples.GetAllSinceLastCall(None, self.m_fieldGroup).values

        #remove last set of label values
        for gpuId in fvs.keys():
            gpuUuid = self.m_gpuIdToUUId[gpuId]
            gpuBusId = self.m_gpuIdToBusId[gpuId]
            gpuUniqueId = gpuUuid if dcgm_config['sendUuid'] else gpuBusId
            for fieldId in self.m_publishFields[self.m_updateFreq]:
                if fieldId in self.m_dcgmIgnoreFields:
                    continue
                self.m_gauges[fieldId].remove(gpuId,gpuUniqueId,dcgm_config['jobId'])
        #update job id
        with open('curr_jobID') as f:
            dcgm_config['jobId'] = f.readline().strip()
        logging.debug('Job ID updated to %s',dcgm_config['jobId'])

    def Loop(self):
        global job_update
        job_update=False
        try:
            while True:
                if(job_update):
                    self.jobID_update()                
                self.Process()
                time.sleep(0.1)                
                if dcgm_config['exit'] == True:
                    logging.info('Received exit signal, shutting down ...')
                    break
        except KeyboardInterrupt:
            pass


def init_config():
    global dcgm_config
    dcgm_config = {
        'exit': False,
        'ignoreList': [],
        'dcgmHostName': None,
        'prometheusPort': None,
        'prometheusPublishInterval': None,
        'publishFieldIds': None,
    }


def init_signal_handler():
    def exit_handler(signalnum, frame):
        dcgm_config['exit'] = True
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)


def parse_dcgm_cli():
    parser = dcgm_client_cli_parser.create_parser(
        name='prometheus',
        field_ids=DCGM_FIELDS,
        interval=1,
        publish_port=8000,
        log_level='INFO',
    )
    parser.add_argument('-m','--profiler_metrics',action='store_true', help='Enable profile metrics (Tensor Core,FP16,FP32,FP64 activity). Addition of profile metrics encurs additional overhead on computer nodes.')
     
    args = dcgm_client_cli_parser.run_parser(parser)
    #add profiling metrics if flag enabled
    if(args.profiler_metrics) :
        args.field_ids.extend(DCGM_PROF_FIELDS)
    field_ids = dcgm_client_cli_parser.get_field_ids(args)
    numeric_log_level = dcgm_client_cli_parser.get_log_level(args)

    # Defaults to localhost, so we need to set it to None.
    if args.embedded:
        dcgm_config['dcgmHostName'] = None
    else:
        dcgm_config['dcgmHostName'] = args.hostname
    dcgm_config['prometheusPort'] = args.publish_port
    dcgm_config['prometheusPublishInterval'] = args.interval
    dcgm_config['publishFieldIds'] = field_ids
    dcgm_config['sendUuid'] = True
    dcgm_config['jobId'] = None
    dcgm_config['profilerMetrics'] = args.profiler_metrics
    logging.basicConfig(
        level=numeric_log_level,
        filemode='w+',
        format='%(asctime)s %(levelname)s: %(message)s',
    )


def main():
    init_config()
    init_signal_handler()
    parse_dcgm_cli()

    exporter = DcgmExporter()
    exporter.Loop()
    exporter.Shutdown()


if __name__ == '__main__':
    main()
