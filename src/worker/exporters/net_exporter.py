import os
import sys
import time
import signal
import logging
import argparse

import prometheus_client

IB_COUNTERS = [
    'port_xmit_data',
    'port_rcv_data',
    'port_xmit_discards',
    'port_rcv_errors',
    'port_xmit_constraint_errors',
    'port_rcv_constraint_errors',
    'link_downed',
]


def watch(f):
    while True:
        f.seek(0)
        time.sleep(0.1)
        yield f.readline()


class NetExporter():
    def __init__(self):
        self.init_connection()
        self.init_gauges()           
        signal.signal(signal.SIGUSR1,self.jobID_update_flag)

    def init_connection(self):
        prometheus_client.start_http_server(config['listen_port'])
        logging.info('Started prometheus client')

        field_list = []
        field_list.extend(IB_COUNTERS)
        logging.info('Publishing fields: {}'.format(','.join(field_list)))

    def init_gauges(self):
        self.guages = {}
        for field_name in IB_COUNTERS:
            self.guages[field_name] = prometheus_client.Gauge(
                'ib_{}'.format(field_name),
                'ib_{}'.format(field_name),
                ['ib_port', 'ib_sys_guid','job_id']
            )


    def process(self):
        for ib_port in config['ib_port'].keys():
            ib_port_config = config['ib_port'][ib_port]
            for field_name in IB_COUNTERS:
                ib_port_config['counter_file'][field_name].seek(0)
                counter = int(ib_port_config['counter_file']
                              [field_name].readline().strip())
                if field_name.endswith('_data'):
                    counter_delta = counter - ib_port_config['counters'][field_name]
                    if counter_delta >= 0:
                        self.handle_field(
                            ib_port,
                            field_name,
                            counter_delta * 4 / config['update_freq'],
                        )
                    else:
                        self.handle_field(
                            ib_port,
                            field_name,
                            (counter_delta + 2**64) * 4 / config['update_freq'],
                        )
                else:
                    self.handle_field(ib_port, field_name, counter)
                ib_port_config['counters'][field_name] = counter

    def handle_field(self, ib_port, field_name, value):
        self.guages[field_name].labels(
            ib_port,
            config['ib_port'][ib_port]['sys_image_guid'],
            config['job_id'],
        ).set(value)
        logging.debug('Sent InfiniBand %s %s : %s=%s', ib_port,
                      config['ib_port'][ib_port]['sys_image_guid'], field_name,
                      str(value))

    def jobID_update_flag(self, signum, stack):
        '''Sets job update flag when user defined signal comes in'''
        global job_update
        job_update=True
            
    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        global job_update
        job_update=False
        #remove last set of label values        
        for ib_port in config['ib_port'].keys():
            for field_name in IB_COUNTERS:
                self.guages[field_name].remove(ib_port,config['ib_port'][ib_port]['sys_image_guid'],config['job_id'])                          
        #update job id
        with open('curr_jobID') as f:
            config['job_id'] = f.readline().strip()
        logging.debug('Job ID updated to %s',config['job_id'])      

    def loop(self):
        global job_update
        job_update=False
        try:
            while True:
                if(job_update):
                    self.jobID_update()
                self.process()
                time.sleep(config['update_freq'])
                if config['exit'] == True:
                    logging.info('Received exit signal, shutting down ...')
                    for ib_port in config['ib_port'].keys():
                        for field_name in IB_COUNTERS:
                            config['ib_port'][ib_port]['counter_file'][
                                field_name].close()
                    break
        except KeyboardInterrupt:
            pass


def init_config(job_id):
    global config
    config = {
        'exit': False,
        'update_freq': 0.1,
        'listen_port': 8001,
        'publish_interval': 1,
        'ib_port': {},
        'job_id': job_id
    }


# /sys/class/net/eth0/statistics/rx_bytes
def init_infiniband():
    sysfs_path = '/sys/class/infiniband'
    for hca in os.listdir(sysfs_path):
        sys_image_guid = ''
        with open(os.path.join(sysfs_path, hca, 'sys_image_guid')) as f:
            sys_image_guid = f.readline().strip().replace(':', '')
        for port in os.listdir(os.path.join(sysfs_path, hca, 'ports')):
            counter_path = os.path.join(sysfs_path, hca, 'ports', port,
                                        'counters')
            counter_file = {}
            counters = {}
            
            for field_name in IB_COUNTERS:
                counter_file[field_name] = open(
                    os.path.join(counter_path, field_name), 'r')
                counters[field_name] = int(
                    counter_file[field_name].readline().strip())
            config['ib_port']['{}:{}'.format(hca, port)] = {
                'sys_image_guid': sys_image_guid,
                'counter_path': counter_path,
                'counter_file': counter_file,
                'counters': counters,
            }


def init_signal_handler():
    def exit_handler(signalnum, frame):
        config['exit'] = True
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

def get_log_level(loglevel):
    levelStr = loglevel.upper()
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
        print ("Could not understand the specified --log-level '%s'" % (args.loglevel))
        args.print_help()
        sys.exit(2)
    return numeric_log_level

def main(args):
    logging.basicConfig(level=get_log_level(args.log_level))
    jobId=None
    init_config(jobId)
    init_infiniband()
    init_signal_handler()

    exporter = NetExporter()
    exporter.loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", default='INFO', help='Specify a log level to use for logging. CRITICAL (0) - \
                        log only critical errors that drastically affect \
                        execution ERROR (1) - Log any error in execution \
                        WARNING (2) - Log all warnings and errors that occur \
                        INFO (3) - Log informational messages about program \
                        execution in addition to warnings and errors DEBUG (4) \
                        - Log debugging information in addition to all')
    args = parser.parse_args()
    main(args)
