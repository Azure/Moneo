import sys
import os
import signal
import logging
import argparse
import subprocess
import shlex
import time
import re
import prometheus_client
import json

FIELD_LIST = []
metrics_list = []
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

def init_ib_config():
    # IB mapping
    cmd = 'ibv_devinfo -l'
    result = shell_cmd(cmd, 5)
    if 'HCAs found' in result or 'HCA found' in result:
        try:
            result = result.split('\n')[1:]
            for idx, ib in enumerate(result):
                if "ib" not in ib:
                    continue
                if len(ib):
                    mapping = re.search(r"ib\d", ib.strip()).group()
                    IB_Mapping[mapping] = ib.strip() + ':1'
                    config['ib_port'][str(idx)] = ib.strip() + ':1'
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
                config['gpu_id'][str(gpu)] = str(gpu)
        except Exception as e:
            print(e)
            pass


class CustomExporter():
    '''Example custom node exporter'''

    def __init__(self, custom_metrics_file_path):
        '''initializes parent class'''
        self.custom_metrics_file_path = custom_metrics_file_path
        self.init_connection()
        self.init_gauges()
        signal.signal(signal.SIGUSR1, self.jobID_update_flag)

    def init_connection(self):
        prometheus_client.start_http_server(config['listen_port'])
        logging.info('Started prometheus client')

        self.field_list = [] 
        self.field_list.extend(FIELD_LIST)
        logging.info('Publishing fields: {}'.format(','.join(self.field_list)))

    def init_gauges(self):
        '''Initialization of Prometheus parameters.
        Override in Child Class if needed'''
        self.gauges = {}
        for field_name in self.field_list:
            metric_name = ''
            if "gpu_" in field_name:
                metric_name = field_name.split('_')[0] + '_' + field_name.split('_')[-1]
                if metric_name in metrics_list:
                    continue
                self.gauges[metric_name] = prometheus_client.Gauge(
                    'custom_{}'.format(metric_name),
                    'custom_{}'.format(metric_name),
                    ['gpu_id', 'job_id']
                )
            elif "ib_" in field_name:
                metric_name = field_name.split('_')[0] + '_' + field_name.split('_')[2]
                if metric_name in metrics_list:
                    continue
                self.gauges[metric_name] = prometheus_client.Gauge(
                    'custom_{}'.format(metric_name),
                    'custom_{}'.format(metric_name),
                    ['ib_port', 'job_id']
                ) 
            else:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'custom_{}'.format(field_name),
                    'custom_{}'.format(field_name),
                    ['job_id']
                )
            if metric_name != '' and metric_name not in metrics_list:
                metrics_list.append(metric_name)
                logging.info('Publishing metric: {}'.format(metric_name))

    def collect_custom_metrics(self):
        '''Updates custom metrics'''
        if os.path.exists(self.custom_metrics_file_path):
            with open(self.custom_metrics_file_path, 'r') as f:
                return json.load(f)
        else:
            logging.error('Custom metrics file does not exist. Exiting...')
            sys.exit(1)

    def process(self):
        custom_metrics = self.collect_custom_metrics()
        for node_field in self.field_list:
            value = custom_metrics[node_field] if node_field in custom_metrics.keys() else None
            if not value:
                continue
            self.handle_field(node_field, value)

    def update_gauges_field(self, field_name, value, config):
        if "gpu_" in field_name:
            gpu_idx = field_name.split('_')[1]
            metric_name = field_name.split('_')[0] + '_' + field_name.split('_')[2]
            if int(gpu_idx) < len(GPU_Mapping):
                self.gauges[metric_name].labels(
                    config['gpu_id'][gpu_idx],
                    config['job_id']
                ).set(value)
        elif "ib_" in field_name:
            ib_port = field_name.split('_')[1]
            metric_name = field_name.split('_')[0] + '_' + field_name.split('_')[2]
            if int(ib_port) < len(IB_Mapping):
                self.gauges[metric_name].labels(
                    config['ib_port'][ib_port],
                    config['job_id']
                ).set(value)
        else:
            self.gauges[field_name].labels(
                config['job_id']
            ).set(value)

    def handle_field(self, field_name, value):  # noqa: C901
        '''Update metric value for gauge'''
        self.update_gauges_field(field_name, value, config)
        logging.debug('Custom exporter field %s: %s', field_name, str(value))

    def remove_metric(self, field_name):
        """Remove mertics label values"""
        if "gpu_" in field_name:
            gpu_idx = field_name.split('_')[1]
            metric_name = field_name.split('_')[0] + field_name.split('_')[2]
            if int(gpu_idx) < len(GPU_Mapping):
                self.gauges[metric_name].remove(config['gpu_id'][gpu_idx], config['job_id'])
        elif "ib_" in field_name:
            ib_port = field_name.split('_')[1]
            metric_name = field_name.split('_')[0] + field_name.split('_')[2]
            if int(ib_port) < len(IB_Mapping):
                ib_port = field_name.split('_')[1]
            self.gauges[metric_name].remove(config['ib_port'][ib_port], config['job_id'])
        else:
            self.gauges[field_name].remove(config['job_id'])

    def jobID_update_flag(self, signum, stack):
        '''Sets job update flag when user defined signal comes in'''
        global job_update
        job_update = True

    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        # Remove last set of label values
        for field_name in self.field_list:
            self.remove_metric(field_name)

        # Update job id
        with open('/tmp/moneo-worker/curr_jobID') as f:
            config['job_id'] = f.readline().strip()
        logging.debug('Job ID updated to %s', config['job_id'])

    # This is called at the termination of the application.
    # Can be used to close any open files.
    def cleanup(self):
        '''Things that need to be called when signal to exit is given'''
        logging.info('Received exit signal, shutting down ...')

    def loop(self):
        global job_update
        job_update = False
        try:
            while True:
                if (job_update):
                    self.jobID_update()
                self.process()
                time.sleep(config['update_freq'])
                if config['exit'] is True:
                    logging.info('Received exit signal, shutting down ...')
                    break
        except KeyboardInterrupt:
            pass

# you will need to initialize your custom metric's file if we are exporting
# from a file you may also want to initialize the config's counter member
# for the specific field
def init_config(job_id, port=None):
    '''Example of config initialization'''
    global config
    if not port:
        port = 8003
    config = {
        'exit': False,
        'update_freq': 1,
        'listen_port': port,
        'publish_interval': 1,
        'gpu_id': {},
        'ib_port': {},
        'job_id': job_id,
    }

def init_custom_metrics(custom_metcis_file_path):
    '''Example of custom metrics initialization'''
    metrics_json_path = custom_metcis_file_path
    if not os.path.exists(metrics_json_path):
        logging.error('Custom metrics file does not exist. Exiting...')
        sys.exit(1)
    with open(metrics_json_path) as f:
        custom_metrics = json.load(f)

    for metrics_name, _ in custom_metrics.items():
        FIELD_LIST.append(metrics_name)

# You can just copy paste this function. Used to handle signals
def init_signal_handler():
    '''Handles exit signals, User defined signale defined in Base class'''
    def exit_handler(signalnum, frame):
        config['exit'] = True
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

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
    parser.add_argument(
        "--custom_metrics_file_path",
        type=str,
        default=None,
        help='Path to custom metrics file')
    args = parser.parse_args()
    # set up logging
    os.makedirs('/tmp/moneo-worker', exist_ok=True)
    logging.basicConfig(level=get_log_level(args), filename='/tmp/moneo-worker/moneoExporter.log',
                        format='[%(asctime)s] node_exporter-%(levelname)s-%(message)s')
    jobId = None  # set a default job id of None
    # try:
    init_config(jobId, args.port)
    init_custom_metrics(args.custom_metrics_file_path)
    init_signal_handler()
    init_nvidia_config()
    init_ib_config()
    exporter = CustomExporter(args.custom_metrics_file_path)
    exporter.loop()
    # except Exception as e:
    #     logging.error('Raised exception. Message: %s', e)


if __name__ == '__main__':
    main()
