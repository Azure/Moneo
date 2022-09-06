import os
import sys
import time
import signal
import logging
import argparse

import prometheus_client

class BaseExporter:
    '''Base exporter'''

    def __init__(self,node_fields):
        self.node_fields = node_fields
        self.init_connection()
        self.init_gauges()       
        signal.signal(signal.SIGUSR1,self.jobID_update_flag)


    def init_connection(self):
        prometheus_client.start_http_server(config['listen_port'])
        logging.info('Started prometheus client')
        logging.info('Publishing fields: {}'.format(','.join(self.node_fields)))


    def init_gauges(self):
        '''Initialization of Prometheus parameters. Override in Child Class if needed'''      
        self.guages = {}
        for field_name in NODE_FIELDS:
            self.guages[field_name] = prometheus_client.Gauge(
                'ib_{}'.format(field_name),
                'ib_{}'.format(field_name),
                ['job_id']
            )


    def collect(self,field_name):
        '''default collection Method'''
        raise NotImplementedError('Must implement this method')
        return value


    def process(self):
        print("")
        for field_name in field_name:
            self.collect(field_name)
        handle_field(self, field_name, value)

    def handle_field(self, field_name, value):
        self.guages[field_name].labels(
            config['job_id'],
        ).set(value)


    def jobID_update_flag(self, signum, stack):
        '''Sets job update flag when user defined signal comes in'''
        global job_update
        job_update=True


    def jobID_update(self):
        '''Updates job id when job update flag has been set'''
        global job_update
        job_update=False
        #remove last set of label values        
        for field_name in self.node_fields:
            self.guages[field_name].remove(ib_port,config['ib_port'][ib_port]['sys_image_guid'],config['job_id'])                          
        #update job id
        with open('curr_jobID') as f:
            config['job_id'] = f.readline().strip()
        logging.debug('Job ID updated to %s',config['job_id'])    


    def cleanup(self):
        raise NotImplementedError('Must implement this method')


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
                    self.cleanup()
                    break
        except KeyboardInterrupt:
            pass
