import os
import sys
import time
import signal
import logging
import argparse
from base_exporter import BaseExporter
import prometheus_client

FIELD_LIST = {}

class NodeExporter(BaseExporter):
    def _init_(self):
        super.init


def init_config(job_id),port=None:
    global config
    if not port:
        port=8002
    config = {
        'exit': False,
        'update_freq': 1,
        'listen_port': port,
        'publish_interval': 1,
        'job_id': job_id
        'fieldFiles':{}
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_level", default='INFO', help='Specify a log level to use for logging. CRITICAL (0) - \
                        log only critical errors that drastically affect \
                        execution ERROR (1) - Log any error in execution \
                        WARNING (2) - Log all warnings and errors that occur \
                        INFO (3) - Log informational messages about program \
                        execution in addition to warnings and errors DEBUG (4) \
                        - Log debugging information in addition to all')
    parser.add_argument("-p","--port", type=int,default=None, help='Port to export metrics from')
    args = parser.parse_args()
    
    logging.basicConfig(level=get_log_level(args.log_level))
    jobId=None
    init_config(jobId,args.port)
    init_signal_handler()

    exporter = BaseExporter(FIELD_LIST)
    exporter.loop()


if __name__ == '__main__':
    main()