import os
import sys
import time
import signal
import logging

import prometheus_client

IB_COUNTERS = [
    'port_xmit_data',
    'port_rcv_data',
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
                ['ib_port', 'ib_sys_guid'],
            )

    def process(self):
        for ib_port in config['ib_port'].keys():
            ib_port_config = config['ib_port'][ib_port]
            for field_name in IB_COUNTERS:
                ib_port_config['counter_file'][field_name].seek(0)
                counter = int(ib_port_config['counter_file']
                              [field_name].readline().strip())
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
                ib_port_config['counters'][field_name] = counter

    def handle_field(self, ib_port, field_name, value):
        self.guages[field_name].labels(
            ib_port,
            config['ib_port'][ib_port]['sys_image_guid'],
        ).set(value)
        logging.debug('Sent InfiniBand %s %s : %s=%s', ib_port,
                      config['ib_port'][ib_port]['sys_image_guid'], field_name,
                      str(value))

    def loop(self):
        try:
            while True:
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


def init_config():
    global config
    config = {
        'exit': False,
        'update_freq': 0.1,
        'listen_port': 8001,
        'publish_interval': 1,
        'ib_port': {},
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


def main():
    logging.basicConfig(level=logging.INFO)
    init_config()
    init_infiniband()
    init_signal_handler()

    exporter = NetExporter()
    exporter.loop()


if __name__ == '__main__':
    main()
