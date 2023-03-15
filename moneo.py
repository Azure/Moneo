# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import os
import logging
import subprocess
import shlex

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

def parallel_ssh_check():
    """check parallel ssh installed"""

    os_type = shell_cmd( 'awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)
    
    if 'Ubuntu' in os_type:
        pkg_check_results = shell_cmd( 'dpkg -s pssh', 45)
    else:
        pkg_check_results = shell_cmd( 'rpm -q pssh', 45)

    if 'not installed' in pkg_check_results:
        logging.error('pssh is not installed, please install pssh to continue')
        print('pssh is not installed, please install pssh to continue')
        exit(1)
    return True

def pssh(cmd, hosts_file, timeout=300, max_threads=16):
    pssh_cmd = 'pssh'
    os_type = shell_cmd( 'awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)
    if 'Ubuntu' in os_type:
        pssh_cmd = 'parallel-ssh'
    pssh_cmd =  pssh_cmd + " -i -t 0 -p {} -h {} 'sudo {}' ".format(max_threads, hosts_file, cmd)

    out = shell_cmd(pssh_cmd, timeout)
    print(out)


def pscp(copy_path, destination_dir, hosts_file, timeout=300, max_threads=16):
    pscp_cmd = 'pscp.pssh'
    os_type = shell_cmd( 'awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)
    if 'Ubuntu' in os_type:
        pscp_cmd = 'parallel-scp'

    pscp_cmd =  pscp_cmd + " -r -t 0 -p {} -h {} {} {}".format(max_threads, hosts_file, copy_path, destination_dir)

    out = shell_cmd(pscp_cmd, timeout)
    print(out)


def deploy_worker(hosts_file,max_threads=16):
    pssh(cmd='rm -rf /tmp/moneo-worker', hosts_file=hosts_file)
    moneo_dir = os.path.dirname(os.path.realpath(__file__))
    copy_path='./src/worker/'
    destination_dir='/tmp/moneo-worker'
    print('-Copying files to workers-')
    out = pscp(copy_path, destination_dir, hosts_file)
    print(out)
    print('--------------------------')
    print('-Running install on workers-')
    out = pssh(cmd='/tmp/moneo-worker/install/install.sh', hosts_file=hosts_file, max_threads=max_threads)
    print(out)
    print('--------------------------')




class MoneoCLI:
    '''Moneo CLI call'''

    def __init__(self, args):
        '''Init for MoneoCLI'''
        self.args = args

    def deploy(self):
        '''
        Deploys Moneo monitoring to hosts listed in the
        specified host ini file
        '''
        dep_cmd = 'ansible-playbook' + ' -f ' + str(args.fork_processes) + \
                  ' -i ' + args.host_ini + ' src/ansible/deploy.yaml'

        if self.args.type == 'workers':
            dep_cmd = dep_cmd + ' -e "skip_master=true"'
        elif self.args.type == 'manager':
            dep_cmd = dep_cmd + ' -e "skip_worker=true"'
        dep_cmd = dep_cmd + ' -e "skip_insights=' + \
            ('false' if self.args.insights else 'true') + '"'
        dep_cmd = dep_cmd + ' -e "enable_profiling=' + \
            ('true' if self.args.profiler_metrics else 'false') + '"'
        dep_cmd = dep_cmd + ' -e "enable_container=' + \
            ('true' if self.args.container else 'false') + '"'

        print('Deployment type: ' + self.args.type)
        logging.info('Moneo starting, Deployment type: ' + args.type)
        os.system(dep_cmd)

    def stop(self):
        '''Stops Moneo monitoring on hosts listed in the specified host ini file'''
        while True:
            confirm = input("Are you sure you would like to perform a '" + self.args.type
                            + "' shutdown of Moneo? (Y/n)\n")

            if confirm.upper() == 'Y':
                dep_cmd = 'ansible-playbook' + ' -f ' + str(args.fork_processes) + \
                          ' -i ' + args.host_ini + ' src/ansible/shutdown.yaml'
                if self.args.type == 'workers':
                    dep_cmd = dep_cmd + ' -e "skip_master=true"'
                elif self.args.type == 'manager':
                    dep_cmd = dep_cmd + ' -e "skip_worker=true"'
                os.system(dep_cmd)
                print("Moneo is Shutting down \n")
                logging.info('Moneo is Shutting down')
                return 0

            elif confirm.upper() == 'N':
                print("Canceling request to shutdown Moneo \n")
                logging.info('Canceling request to shutdown Moneo')
                return 0
            else:
                print("Input not recognized\n")

    def jobID_update(self):
        '''Updates job id for hosts listed in the specified host ini file'''
        dep_cmd = 'ansible-playbook' + ' -f ' + str(args.fork_processes) + ' -i ' + \
            args.host_ini + ' src/ansible/updateJobID.yaml -e job_Id=' + args.job_id
        print('Job ID update to ' + self.args.job_id)
        logging.info('Job ID update to ' + args.job_id + ". Hostfile: " + args.host_ini)
        os.system(dep_cmd)


def check_deploy_shutdown(args, parser):
    '''
    Checks if the necessary arguments are provided for
    deploy and shutdwon
    '''
    if (not os.path.isfile(args.host_ini)):
        print(args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.\n")
        parser.print_help()
        exit(1)
    if args.job_id:
        print(
            "Job Id cannot be specified during deployment and shutdown. Ignoring Job Id.\n")
    choices = ['manager', 'workers', 'full']
    if (args.type not in choices):
        print('Deployment/shutdown type not recognized or entered. Defaulted to the full option.\n')
        args.type = 'full'


def check_insights_config(args, parser):
    if (args.insights and not os.path.isfile('config.ini')):
        print('The Application Insights configuration file (config.ini) does not exist.'
              'Please provide one to use this feature.')
        parser.print_helper()
        exit(1)


if __name__ == '__main__':
    if parallel_ssh_check():
        print('pssh installed')
    hosts_file='/home/rafsalas/Moneo/hosts.ini'
    pssh(cmd='hostname',hosts_file=hosts_file)
    deploy_worker(hosts_file=hosts_file)
    exit()
    #   parser options
    parser = argparse.ArgumentParser(
        description='Moneo CLI Help Menu',
        prog='moneo.py',
        usage='%(prog)s [-d ] [-c HOST_INI] [{manager,workers,full}] \
        \nusage: %(prog)s [-s ] [-c HOST_INI] [{manager,workers,full}] \
        \nusage: %(prog)s [-j JOB_ID ] [-c HOST_INI] \
        \ni.e. python3 moneo.py -d -c ./host.ini full'
    )

    parser.add_argument(
        '-c',
        '--host_ini',
        default='./host.ini',
        help='Provide filepath and name of ansible config file. The default is host.ini in the Moneo directory.')
    parser.add_argument(
        '-j',
        '--job_id',
        type=str,
        help='Job ID for filtering metrics by job group. Host.ini file required.'
             'Cannot be specified during deployment and shutdown')
    parser.add_argument(
        '-d',
        '--deploy',
        action='store_true',
        help='Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument(
        '-s',
        '--shutdown',
        action='store_true',
        help='Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument(
        '-i',
        '--insights',
        action='store_true',
        help='Experimental feature: Enable exporting of metrics to Azure Insights.'
             'Requires a valid instrumentation key and base_url for the Prometheus DB in config.ini')
    parser.add_argument(
        'type',
        metavar='type',
        type=str,
        default='full',
        nargs="?",
        help='Type of deployment/shutdown. Choices: {manager,workers,full}. Default: full.')
    parser.add_argument(
        '-p',
        '--profiler_metrics',
        action='store_true',
        default=False,
        help='Enable profile metrics (Tensor Core,FP16,FP32,FP64 activity).'
             'Addition of profile metrics encurs additional overhead on computer nodes.')
    parser.add_argument(
        '-r',
        '--container',
        action='store_true',
        default=False,
        help='Deploy Moneo-worker inside the container.')
    parser.add_argument(
        '-f',
        '--fork_processes',
        default=16,
        type=int,
        help='The number of processes used to deploy/shutdown/update Moneo.'
             'Increasing process count can reduce the latency when deploying to large number of nodes. Default is 16.')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, filename='./moneoCLI.log', format='[%(asctime)s] moneoCLI-%(levelname)s-%(message)s')
    try:
        mCLI = MoneoCLI(args)

        #   Workflow selection
        if (args.deploy and args.shutdown):
            print("deploy and shutdown are exclusive arguments. Please only provide one.\n")
            parser.print_help()
            exit(1)
        elif args.deploy:
            check_deploy_shutdown(args, parser)
            check_insights_config(args, parser)
            mCLI.deploy()
        elif args.shutdown:
            check_deploy_shutdown(args, parser)
            mCLI.stop()
        elif args.job_id:
            if (not os.path.isfile(args.host_ini)):
                print(
                    args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.\n")
                parser.print_help()
                exit(1)
            mCLI.jobID_update()
        else:
            parser.print_help()
    except Exception as e:
        logging.error('Raised exception. Message: %s', e)

    exit(0)
