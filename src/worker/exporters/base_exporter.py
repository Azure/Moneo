import time
import signal
import logging

import prometheus_client


class BaseExporter:
    '''Base exporter'''

    def __init__(self, node_fields, config):
        '''Initialization of the base class'''
        self.node_fields = node_fields
        self.config = config
        self.init_connection()
        self.init_gauges()

        signal.signal(signal.SIGUSR1, self.jobID_update_flag)

    def init_connection(self):
        '''Set up connection for the port specified on the config dict'''
        prometheus_client.start_http_server(self.config['listen_port'])
        logging.info('Started prometheus client')
        logging.info('Publishing fields: {}'.format(','.join(self.node_fields)))

    def init_gauges(self):
        '''Initialization of Prometheus parameters. Override in Child Class if needed'''
        self.gauges = {}
        for field_name in self.node_fields:
            self.gauges[field_name] = prometheus_client.Gauge(
                'node_{}'.format(field_name),
                'node_{}'.format(field_name),
                ['job_id']
            )

    def collect(self, field_name):
        '''Default collection method meant to be overiden for child class'''
        raise NotImplementedError('Must implement this method')
        return field_name

    def process(self):
        '''Perform metric collection'''
        for field_name in self.node_fields:
            value = self.collect(field_name)
            self.handle_field(field_name, value)

    def handle_field(self, field_name, value):
        '''Update metric value for gauge'''
        self.gauges[field_name].labels(
            self.config['job_id'],
        ).set(value)
        logging.debug('Node exporter field %s: %s', field_name, str(value))

    def jobID_update_flag(self, signum, stack):
        '''Sets job update flag when user defined signal comes in'''
        global job_update
        job_update = True

    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        global job_update
        job_update = False
        # remove last set of label values
        for field_name in self.node_fields:
            self.gauges[field_name].remove(self.config['job_id'])
        # update job id
        with open('curr_jobID') as f:
            self.config['job_id'] = f.readline().strip()
        logging.debug('Job ID updated to %s', self.config['job_id'])

    def cleanup(self):
        '''Clean up method must be overridden '''
        raise NotImplementedError('Must implement this method')

    def loop(self):
        '''Main work loop which should be called in main'''
        global job_update
        job_update = False
        try:
            while True is True:
                if job_update:
                    self.jobID_update()
                self.process()
                time.sleep(self.config['update_freq'])
                if self.config['exit'] is True:
                    logging.info('Received exit signal, shutting down ...')
                    self.cleanup()
                    break
        except KeyboardInterrupt:
            pass
