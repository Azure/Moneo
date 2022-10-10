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
import signal
import logging
import argparse
from base_exporter import BaseExporter
import subprocess
import shlex
import psutil

import prometheus_client

FIELD_LIST = [
    'net_rx',
    'net_tx',
    'cpu_util',  # use /proc/stat
    'cpu_frequency',  # use /proc/cpuinfo
    # 'mem_free',  # use /proc/meminfo
    'mem_available',  # use /proc/meminfo
    # 'mem_used',  # use /proc/meminfo
    'mem_util'  # use /proc/meminfo
]

CPU_PROF_FIELDS = [
    'cpu_times_user',  # use /proc/stat
    'cpu_times_system',  # use /proc/stat
    'cpu_times_idle',  # use /proc/stat
    'cpu_times_iowait'  # use /proc/stat
]


# feel free to copy and paste if os commands are needed
def shell_cmd(args, timeout):
    """Helper Function for running subprocess"""
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
            else:
                self.gauges[field_name] = prometheus_client.Gauge(
                    'node_{}'.format(field_name),
                    'node_{}'.format(field_name),
                    ['job_id']
                )
        print(self.gauges)

    # example function of how to collect metrics from a command using the
    # shell_cmd helper function the parent class will call this collect
    # function to update the Prometheus gauges
    def collect(self, field_name):
        '''Custom collection Method'''
        value = None
        if field_name == self.node_fields[0]:
            cmd = "grep 'eth0' " + self.config['fieldFiles'][field_name]
            args = shlex.split(cmd)
            value = shell_cmd(args, 5).split()[1]  # 1 is the column for recv bytes
            delta = int(value) - int(self.config['counter'][field_name])
            self.config['counter'][field_name] = value
            value = delta / (self.config['update_freq'])  # bandwidth

        elif field_name == self.node_fields[1]:
            cmd = "grep 'eth0' " + self.config['fieldFiles'][field_name]
            args = shlex.split(cmd)
            value = shell_cmd(args, 5).split()[9]  # 9 is the column for tx bytes
            delta = int(value) - int(self.config['counter'][field_name])
            self.config['counter'][field_name] = value
            value = delta / (self.config['update_freq'])  # bandwidth

        elif 'cpu' in field_name:
            value = {}
            if 'times' in field_name or 'util' in field_name:
                # If using psutil, times % and util % do not need to be
                # calculated using the counters

                if 'times' in field_name:
                    for id, time_percents in enumerate(psutil.cpu_times_percent(percpu=True)):
                        attribute = field_name.split('_')[-1]
                        value[str(id)] = getattr(time_percents, attribute)

                else:  # CPU Util %
                    for id, util_percent in enumerate(psutil.cpu_percent(percpu=True)):
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

        else:
            value = 0

        return value

    def handle_field(self, field_name, value):
        '''Update metric value for gauge'''
        if 'cpu' in field_name:
            logging.debug(f'Handeling field: {field_name}')
            for id, k in enumerate(value.keys()):
                numa_domain = str(id//config['numa_domain_size'])
                logging.debug(f'Handeling key: {k}. Setting value: {value[k]}')
                self.gauges[field_name].labels(
                    job_id=self.config['job_id'],
                    cpu_id=k,
                    numa_domain=numa_domain
                ).set(value[k])
        else:
            self.gauges[field_name].labels(
                self.config['job_id'],
            ).set(value)
            logging.debug('Node exporter field %s: %s', field_name, str(value))

    # This is called at the termination of the application.
    # Can be used to close any open files.
    def cleanup(self):
        '''Things that need to be called when signal to exit is given'''
        logging.info('Received exit signal, shutting down ...')


# you will need to initialize your custom metric's file if we are exporting
# from a file you may also want to initialize the config's counter member
# for the specific field
def init_config(job_id, port=None, profiler_metrics=False):
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
        'counter': {}
    }

    # get NUMA domain
    cores = psutil.cpu_count()
    cmd = "lscpu"
    args = shlex.split(cmd)
    numa_domains = int(shell_cmd(args, 5).split("\n")[8].split()[-1])
    domain_size = cores//numa_domains
    config['numa_domain_size'] = domain_size

    # Add profiler metrics    
    if profiler_metrics:
        FIELD_LIST.extend(CPU_PROF_FIELDS)

    # initalize field specific config parameters
    for field_name in FIELD_LIST:
        if 'net' in field_name:
            config['fieldFiles'][field_name] = '/proc/net/dev'
            # initialize counter, this will ensure a initial value is present to calculate bandwidth
            cmd = "grep 'eth0' " + config['fieldFiles'][field_name]
            args = shlex.split(cmd)
            if field_name == 'net_rx':
                config['counter'][field_name] = shell_cmd(args, 5).split()[1]
            elif field_name == 'net_tx':
                config['counter'][field_name] = shell_cmd(args, 5).split()[9]

        if 'cpu' in field_name:
            if 'times' in field_name or 'util' in field_name:
                config['fieldFiles'][field_name] = '/proc/stat'

                # Call cpu_percent to get intial 0.0 values
                if 'util' in field_name:
                    _ = psutil.cpu_percent(percpu=True)

            elif 'frequency' in field_name:
                config['fieldFiles'][field_name] = '/proc/cpuinfo'

        if 'mem' in field_name:
            config['fieldFiles'][field_name] = '/proc/meminfo'

        # logging.debug(f"Initialized field: {field_name}, with: {config['counter'][field_name]}\n")


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
        print("Could not understand the specified --log-level '%s'" % (args.loglevel))
        args.print_help()
        sys.exit(2)
    return numeric_log_level


# Copy paste this function, modify if needed
def main():
    '''main function'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", default='INFO', help='Specify a log level to use for logging. CRITICAL (0) - \
                        log only critical errors that drastically affect \
                        execution ERROR (1) - Log any error in execution \
                        WARNING (2) - Log all warnings and errors that occur \
                        INFO (3) - Log informational messages about program \
                        execution in addition to warnings and errors DEBUG (4) \
                        - Log debugging information in addition to all')
    parser.add_argument("-p", "--port", type=int, default=None, help='Port to export metrics from')
    parser.add_argument("-m", "--profiler_metrics", action="store_true", help="Enable profile metrics \
                        (CPU User,System,Idle, IoWait times).")
    args = parser.parse_args()

    logging.basicConfig(level=get_log_level(args))
    jobId = None  # set a default job id of None
    init_config(jobId, args.port, args.profiler_metrics)
    init_signal_handler()

    exporter = NodeExporter(FIELD_LIST, config)
    exporter.loop()


if __name__ == '__main__':
    main()
