######################################################
# This exporter file can be modified or used as
# an example of how to create a custom exporter.
#
# The following files have been modified to
# integrate this exporter:
#    src/ansible/deploy.yaml
#    src/ansible/prometheus.config.j2
#    src/ansible/updateJobID.yaml
#    src/master/prometheus.yml
#    src/worker/shutdown.sh
#
# Modifications to the Grafana dashboard needs
# be done to view metrics exported
# (not done in this example)
######################################################

import sys
import os
import signal
import logging
import argparse
from base_exporter import BaseExporter
import subprocess
import shlex
import psutil
import re
import prometheus_client
from datetime import datetime, timedelta
import json

FIELD_LIST = [
    'net_rx',
    'net_tx',
    'cpu_util',  # use /proc/stat
    'cpu_frequency',  # use /proc/cpuinfo
    'mem_available',  # use /proc/meminfo
    'mem_util'  # use /proc/meminfo
]

GPU_Mapping = {}
IB_Mapping = {}
# feel free to copy and paste if os commands are needed


def shell_cmd(cmd, timeout):
    """Helper Function for running subprocess"""
    args = shlex.split(cmd)
    child = subprocess.Popen(args, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    try:
        result, errs = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        child.kill()
        print("Command " + " ".join(args) + ", Failed on timeout")
        result = 'TimeOut'
        return result
    return result.decode()


class NodeExporter(BaseExporter):
    '''Example custom node exporter'''

    def __init__(self, node_fields, exp_config):
        '''initializes parent class'''
        super().__init__(node_fields, exp_config)

    def init_gauges(self):
        '''Initialization of Prometheus parameters.
           Override in Child Class if needed'''
        self.gauges = {}
        for field_name in self.node_fields:
            if 'cpu' in field_name:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'node_{}'.format(field_name),
                    'node_{}'.format(field_name),
                    ['job_id', 'cpu_id', 'numa_domain']
                )
            elif 'xid' in field_name:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'node_{}'.format(field_name),
                    'node_{}'.format(field_name),
                    ['job_id', 'pci_id', 'gpu_id', 'time_stamp']
                )
            elif 'link_flap' in field_name:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'node_{}'.format(field_name),
                    'node_{}'.format(field_name),
                    ['job_id', 'ib_port', 'time_stamp'])
            else:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'node_{}'.format(field_name),
                    'node_{}'.format(field_name),
                    ['job_id']
                )

    # example function of how to collect metrics from a command using the
    # shell_cmd helper function the parent class will call this collect
    # function to update the Prometheus gauges
    def collect(self, field_name):  # noqa: C901
        '''Custom collection Method'''
        value = None
        if 'net' in field_name:
            cmd = "grep 'eth0' " + self.config['fieldFiles'][field_name]
            val = None
            if 'net_rx' in field_name:
                val = shell_cmd(cmd, 5).split()[1]
            else:  # 'net_tx'
                val = shell_cmd(cmd, 5).split()[9]
            delta = int(val) - int(self.config['counter'][field_name])
            self.config['counter'][field_name] = val
            value = delta / (self.config['update_freq'])  # bandwidth
        elif 'cpu' in field_name:
            value = {}
            if 'util' in field_name:
                for id, util_percent in enumerate(
                        psutil.cpu_percent(percpu=True)):
                    value[str(id)] = util_percent

            elif 'frequency' in field_name:
                for id, freq in enumerate(psutil.cpu_freq(percpu=True)):
                    value[str(id)] = freq.current

        elif 'mem' in field_name:
            metric = field_name.split('_')[-1]
            virtual_mem = psutil.virtual_memory()

            if metric == 'util':
                value = getattr(virtual_mem, 'percent')
            else:
                # psutil returns virtual memory stats in bytes, convert to kB
                value = getattr(virtual_mem, metric) / 1024
        elif 'xid' in field_name or "link_flap" in field_name:
            try:
                value = {}
                cmd = self.config['command'][field_name]
                # check if error present in logs
                field_check = shell_cmd(cmd, 5)
                result = [line for line in field_check.split(
                    '\n') if line.strip() != '']
                for line in result:
                    timestamp = re.search(
                        r"\w\w\w\s+\d+\s\d\d:\d\d:\d\d", line)
                    if not timestamp:
                        continue
                    timestamp = timestamp.group()
                    if 'xid' in field_name:
                        results = re.search(r"\(.+\):\s\d\d", line)
                        if not results:
                            continue
                        results = results.group().split()
                        pci = results[0].replace('(PCI:', '').replace('):', '')[-10:]
                        if pci not in value:
                            value = {pci: {timestamp: []}}
                        if timestamp not in value[pci]:
                            value[pci][timestamp] = []
                        value[pci][timestamp].append(int(results[1].replace(',', '')))
                    else:  # link flap
                        results = re.search(r"\bib\d:", line)
                        if not results:
                            continue
                        hca = results.group().replace(':', '')
                        if hca not in value:
                            value[hca] = []
                        value[hca].append(timestamp)
            except Exception as e:
                logging.error('Raised exception. Message: %s', e)
                pass
        else:
            value = 0
        return value

    def update_field(self, field_name, value, *labels):
        self.gauges[field_name].labels(
            *labels
        ).set(value)

    def handle_field(self, field_name, value):  # noqa: C901
        '''Update metric value for gauge'''
        if 'cpu' in field_name:
            logging.debug(f'Handeling field: {field_name}')
            for id, k in enumerate(value.keys()):
                numa_domain = self.config['cpu_numa_map'][id]
                logging.debug(f'Handeling key: {k}. Setting value: {value[k]}')
                self.update_field(field_name, value[k], self.config['job_id'], k, numa_domain)
        elif 'xid' in field_name or 'link_flap' in field_name:
            Mapping = GPU_Mapping if 'xid' in field_name else IB_Mapping
            try:
                self.remove_metric(field_name, Mapping)
                for dev_id in value.keys():
                    iter_object = value[dev_id].keys() if field_name == 'xid' else value[dev_id]
                    for time_stamp in iter_object:
                        label_values = [self.config['job_id'], dev_id, Mapping[dev_id], time_stamp] \
                            if 'xid' in field_name else [self.config['job_id'], Mapping[dev_id], time_stamp]
                        collect_time = self.config['sample_timestamp'][field_name]
                        event_time = datetime.strptime(time_stamp, "%b %d %H:%M:%S").replace(year=collect_time.year)
                        if event_time <= collect_time:
                            continue
                        if 'xid' in field_name:
                            for code in value[dev_id][time_stamp]:
                                self.update_field(field_name, code, *label_values)
                        else:
                            self.update_field(field_name, 1, *label_values)
                        self.config['counter'][field_name][dev_id].append(time_stamp)
                        self.config['sample_timestamp'][field_name] = event_time
            except Exception as e:
                logging.error('Raised exception. Message: %s', e)
                pass
        else:
            self.update_field(field_name, value, self.config['job_id'])
        logging.debug('Node exporter field %s: %s', field_name, str(value))

    def remove_metric(self, field_name, Mapping):
        if 'cpu' in field_name:
            for id in range(self.config['num_cores']):
                numa_domain = self.config['cpu_numa_map'][id]
                self.gauges[field_name].remove(self.config['job_id'], str(id), numa_domain)
        elif 'xid' in field_name or 'link_flap' in field_name:
            for dev_id in self.config['counter'][field_name].keys():
                for time_stamp in self.config['counter'][field_name][dev_id]:
                    label_values = [self.config['job_id'], dev_id, Mapping[dev_id], time_stamp] if 'xid' in \
                        field_name else [self.config['job_id'], Mapping[dev_id], time_stamp]
                    metric = self.gauges[field_name]
                    labels = {k: v for k, v in zip(metric._labelnames, label_values)}
                    metric_exists = metric.labels(**labels) is not None
                    if metric_exists:
                        self.gauges[field_name].remove(*label_values)
                self.config['counter'][field_name][dev_id].clear()
        else:
            self.gauges[field_name].remove(self.config['job_id'])

    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        # Remove last set of label values
        for field_name in self.node_fields:
            if 'xid' in field_name or 'link_flap' in field_name:
                Mapping = GPU_Mapping if 'xid' in field_name else IB_Mapping
                self.remove_metric(field_name, Mapping)
            else:
                self.remove_metric(field_name, None)
        # Update job id
        with open('/tmp/moneo-worker/curr_jobID') as f:
            self.config['job_id'] = f.readline().strip()
        logging.debug('Job ID updated to %s', self.config['job_id'])

    # This is called at the termination of the application.
    # Can be used to close any open files.
    def cleanup(self):
        '''Things that need to be called when signal to exit is given'''
        logging.info('Received exit signal, shutting down ...')


def get_core_numa_mapping(core_count):
    cmd = 'numactl --hardware'
    output = shell_cmd(cmd, 5)
    numa_mapping = {}
    lines = output.split('\n')
    for line in lines:
        if 'node ' in line and 'cpus' in line:
            current_numa_domain = int(re.search(r'node (\d+)', line).group(1))
            if ':' in line:
                cpus_str = line.split(': ')[1].split()
                for cpu in cpus_str:
                    numa_mapping[int(cpu)] = current_numa_domain
    if len(numa_mapping.keys()) != core_count:
        numa_mapping = {}
        cmd = 'lscpu -e=cpu,node'
        output = shell_cmd(cmd, 5)
        lines = output.split('\n')
        for line in lines:
            if 'CPU' in line.upper() or line.strip() == "":
                continue
            cpu, node = line.split()
            numa_mapping[int(cpu)] = node
    return numa_mapping


# you will need to initialize your custom metric's file if we are exporting
# from a file you may also want to initialize the config's counter member
# for the specific field
def init_config(job_id, port=None):
    '''Example of config initialization'''
    global config
    if not port:
        port = 8002
    config = {
        'exit': False,
        'update_freq': 1,
        'listen_port': port,
        'publish_interval': 1,
        'job_id': job_id,
        'fieldFiles': {},
        'counter': {},
        'sample_timestamp': {},
        'labels': {},
        'columns': {}
    }
    # for xid and link flaps
    config['command'] = {}
    cmd = "awk -F= '/^NAME/{print $2}' /etc/os-release"
    result = shell_cmd(cmd, 5)
    if "Ubuntu" in result:
        config['command']['link_flap'] = "sudo grep 'Lost carrier' /var/log/syslog"
        config['command']['xid_error'] = "sudo grep 'NVRM: Xid' /var/log/syslog"
        init_nvidia_config()
        init_ib_config()

    elif "AlmaLinux" in result:
        config['command']['link_flap'] = "sudo grep 'Lost carrier' /var/log/messages"
        config['command']['xid_error'] = "sudo grep 'NVRM: Xid' /var/log/messages"
        init_nvidia_config()
        init_ib_config()
    else:
        logging.info('OS not supported attempting to continue...')

    # get NUMA domain
    config['num_cores'] = psutil.cpu_count()
    config['cpu_numa_map'] = get_core_numa_mapping(config['num_cores'])

    # initalize field specific config parameters
    for field_name in FIELD_LIST:
        config['sample_timestamp'][field_name] = datetime.now() - timedelta(seconds=5)
        if 'net' in field_name:
            config['fieldFiles'][field_name] = '/proc/net/dev'
            # initialize counter, this will ensure a initial value is present
            # to calculate bandwidth
            cmd = "grep 'eth0' " + config['fieldFiles'][field_name]
            if field_name == 'net_rx':
                config['counter'][field_name] = shell_cmd(cmd, 5).split()[1]
            elif field_name == 'net_tx':
                config['counter'][field_name] = shell_cmd(cmd, 5).split()[9]
        elif 'cpu' in field_name:
            if 'util' in field_name:
                # Call cpu_percent to get intial 0.0 values
                _ = psutil.cpu_percent(percpu=True)


# You can just copy paste this function. Used to handle signals
def init_signal_handler():
    '''Handles exit signals, User defined signale defined in Base class'''
    def exit_handler(signalnum, frame):
        config['exit'] = True
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)


# You can just copy paste this function. This is used to parse the log-level
# argument
def get_log_level(args):
    '''Log level helper'''
    levelStr = args.log_level.upper()
    if levelStr == '0' or levelStr == 'CRITICAL':
        numeric_log_level = logging.CRITICAL
    elif levelStr == '1' or levelStr == 'ERROR':
        numeric_log_level = logging.ERROR
    elif levelStr == '2' or levelStr == 'WARNING':
        numeric_log_level = logging.WARNING
    elif levelStr == '3' or levelStr == 'INFO':
        numeric_log_level = logging.INFO
    elif levelStr == '4' or levelStr == 'DEBUG':
        numeric_log_level = logging.DEBUG
    else:
        print(
            "Could not understand the specified --log-level '%s'" %
            (args.loglevel))
        args.print_help()
        sys.exit(2)
    return numeric_log_level


def init_ib_config():
    global config
    global GPU_Mapping
    global IB_Mapping
    global FIELD_LIST
    # IB mapping
    cmd = 'ibv_devinfo -l'
    result = shell_cmd(cmd, 5)
    if 'HCAs found' in result or 'HCA found' in result:
        try:
            config['counter']['link_flap'] = {}
            result = result.split('\n')[1:]
            for ib in result:
                if "ib" not in ib:
                    continue
                if len(ib):
                    mapping = re.search(r"ib\d", ib.strip()).group()
                    config['counter']['link_flap'][mapping] = []
                    IB_Mapping[mapping] = ib.strip() + ':1'
            FIELD_LIST.append('link_flap')
        except Exception as e:
            print(e)
            pass


def init_nvidia_config():
    global config
    global GPU_Mapping
    global IB_Mapping
    global FIELD_LIST
    # check if nvidiaVM
    nvArch = os.path.exists('/dev/nvidiactl')
    if nvArch:
        config['counter']['xid_error'] = {}
        cmd = 'nvidia-smi -L'
        result = shell_cmd(cmd, 5)
        gpuCount = len(result.split('\nGPU'))
        try:
            for gpu in range(gpuCount):
                cmd = 'nvidia-smi -q -g ' + str(gpu) + ' -d ACCOUNTING'
                result = shell_cmd(cmd, 5)
                pci = re.search(r"\w+:\w\w:\w\w\.", result).group().lower()
                pci = pci.replace('.', '')[-10:]
                GPU_Mapping[pci] = str(gpu)  # pci mapping
                config['counter']['xid_error'][pci] = []
            FIELD_LIST.append('xid_error')
        except Exception as e:
            print(e)
            pass


def init_custom_metric():
    try:
        metric_json_path = '/home/rafsalas/Moneo/custom.json'
        if not os.path.exists(metric_json_path):
            print(f"JSON file '{metric_json_path}' not found.")
            return False
        with open(metric_json_path, 'r') as cmetric_file:
            metric_dict = json.load(cmetric_file)
        gpuCount = 0
        if os.path.exists('/dev/nvidiactl'):
            cmd = 'nvidia-smi -L'
            result = shell_cmd(cmd, 5)
            gpuCount = len(result.split('\nGPU'))
        for metric in metric_dict:
            custom_metric = metric['metric_name'] + "_custom"
            FIELD_LIST.append(custom_metric)
            config['sample_timestamp'][custom_metric] = datetime.now()
            config['fieldFiles'][custom_metric] = metric['counter_file']
            config['command']['custom_metric'] = "sudo tail -n 1 " + config['fieldFiles'][custom_metric]
            if metric['gpu_metric'] == 'true' and gpuCount > 0:
                config['command']['custom_metric'] = "sudo tail -n " + gpuCount + config['fieldFiles'][custom_metric]
                config['counter'][custom_metric] = {i: '' for i in range(gpuCount)}
            config['labels'][custom_metric] = metric['labels']
            config['columns'][custom_metric] = metric['columns_to_extract']
    except Exception as e:
        logging.error('Raised exception. Message: %s', e)
        return False


# Copy paste this function, modify if needed
def main():
    '''main function'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log_level",
        default='INFO',
        help='Specify a log level to use for logging. CRITICAL (0) - \
                        log only critical errors that drastically affect \
                        execution ERROR (1) - Log any error in execution \
                        WARNING (2) - Log all warnings and errors that occur \
                        INFO (3) - Log informational messages about program \
                        execution in addition to warnings and errors DEBUG (4) \
                        - Log debugging information in addition to all')
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=None,
        help='Port to export metrics from')
    args = parser.parse_args()
    # set up logging
    os.makedirs('/tmp/moneo-worker', exist_ok=True)
    logging.basicConfig(level=get_log_level(args), filename='/tmp/moneo-worker/moneoExporter.log',
                        format='[%(asctime)s] node_exporter-%(levelname)s-%(message)s')
    jobId = None  # set a default job id of None
    try:
        init_config(jobId, args.port)
        init_signal_handler()
        exporter = NodeExporter(FIELD_LIST, config)
        exporter.loop()
    except Exception as e:
        logging.error('Raised exception. Message: %s', e)


if __name__ == '__main__':
    main()
