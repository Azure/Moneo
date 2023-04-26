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


def pssh(cmd, hosts_file, timeout=300, max_threads=16, user=None):
    pssh_cmd = 'pssh'
    os_type = shell_cmd('awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)
    if 'Ubuntu' in os_type:  # Ubuntu uses parallel-ssh while centos/AlmaLinux use pssh
        pssh_cmd = 'parallel-ssh'
    if user:
        pssh_cmd = pssh_cmd + " --user={}".format(user)
    pssh_cmd = pssh_cmd + \
        " -x '-o StrictHostKeyChecking=no' -i -t 0 -p {} -h {} 'sudo {}' ".format(max_threads, hosts_file, cmd)
    out = shell_cmd(pssh_cmd, timeout)
    if 'FAILURE' in out:
        raise Exception("Pssh command failed on one or more hosts with command {}, Output: {}".format(pssh_cmd, out))
    return out


def pscp(copy_path, destination_dir, hosts_file, timeout=300, max_threads=16, user=None):
    pscp_cmd = 'pscp.pssh'
    os_type = shell_cmd('awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)
    if 'Ubuntu' in os_type:
        pscp_cmd = 'parallel-scp'
    if user:
        pscp_cmd = pscp_cmd + " --user={}".format(user)
    pscp_cmd = pscp_cmd + \
        " -x '-o StrictHostKeyChecking=no' -r -t \
        0 -p {} -h {} {} {}".format(max_threads, hosts_file, copy_path, destination_dir)
    out = shell_cmd(pscp_cmd, timeout)
    if 'FAILURE' in out:
        raise Exception("Pscp command failed on one or more hosts with command {}, Output: {}".format(pscp_cmd, out))
    return out


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

        print('Deployment type: ' + self.args.type)
        logging.info('Moneo starting, Deployment type: ' + args.type)

        if self.args.type == 'workers' or self.args.type == 'full':
            if self.args.container:
                self.deploy_work_docker(self.args.host_file, self.args.fork_processes)
            else:
                self.deploy_worker(
                    self.args.host_file,
                    self.args.fork_processes)

        if self.args.type == 'manager' or self.args.type == 'full':
            self.deploy_manager(self.args.host_file, user=self.args.user, manager_host=self.args.manager_host, export_Prometheus=self.args.enable_prometheus)
        logging.info('Moneo starting, Deployment type: ' + self.args.type)

    def stop(self):
        '''Stops Moneo monitoring on hosts listed in the specified host ini file'''
        while True:
            confirm = input("Are you sure you would like to perform a '" + self.args.type
                            + "' shutdown of Moneo? (Y/n)\n")
            if confirm.upper() == 'Y':
                if self.args.type == 'workers' or self.args.type == 'full':
                    self.shutdown_worker(self.args.host_file, self.args.fork_processes)
                    print("Moneo workers is Shutting down \n")
                if self.args.type == 'manager' or self.args.type == 'full':
                    self.shutdown_manager(user=self.args.user, manager_host=self.args.manager_host)
                    print("Moneo manager is Shutting down \n")
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
        print('Updating job ID to ' + self.args.job_id)
        logging.info('Updating job ID to ' + self.args.job_id)
        cmd = '/tmp/moneo-worker/jobIdUpdate.sh ' + self.args.job_id
        out = pssh(cmd=cmd, hosts_file=self.args.host_file, user=self.args.user)
        logging.info(out)
        logging.info('Job ID updated to ' + self.args.job_id + ". Hostfile: " + self.args.host_file)

    def deploy_worker(self, hosts_file, max_threads=16):
        '''Deploys Moneo worker to hosts listed in the specified host ini file'''
        out = pssh(cmd='rm -rf /tmp/moneo-worker', hosts_file=hosts_file, user=self.args.user)
        logging.info(out)
        copy_path = './src/worker/'
        destination_dir = '/tmp/moneo-worker'
        print('-Copying files to workers-')
        logging.info('Copying files to workers')
        out = pscp(copy_path, destination_dir, hosts_file, user=self.args.user)
        logging.info(out)
        print('--------------------------')
        if self.args.skip_install:
            pass
        else:
            print('-Installing Moneo on workers-')
            cmd = '/tmp/moneo-worker/install/install.sh'
            if self.args.launch_publisher:
                agent = self.args.launch_publisher
                if agent != 'geneva' and agent != 'azure_monitor':
                    logging.error("Invalid agent specified: " + agent)
                    raise Exception("Invalid agent specified: " + agent)
                print('-Install ' + agent + ' agent-')
                logging.info('Install ' + agent + ' agent')
                cmd = cmd + ' ' + agent
            else:
                cmd = cmd + ' false'
            out = pssh(cmd=cmd, hosts_file=hosts_file, max_threads=max_threads, user=self.args.user)
            logging.info(out)
            print('--------------------------')
        print('-Starting metric exporters on workers-')
        logging.info('Starting metric exporters on workers')
        cmd = '/tmp/moneo-worker/start.sh'
        if self.args.profiler_metrics:
            print('-Profiling enabled-')
            logging.info('Profiling enabled')
            cmd = cmd + ' true'
        else:
            cmd = cmd + ' false'
        if self.args.launch_publisher:
            agent = self.args.launch_publisher
            if agent == 'geneva' and not self.args.publisher_auth:
                logging.error("Geneva agent requires specified authentication")
                raise Exception("Geneva agent requires specified authentication")
            elif agent == 'azure_monitor' and self.args.publisher_auth:
                logging.error("Azure Monitor agent does not require authentication")
                raise Exception("Azure Monitor agent does not require authentication")
            cmd = cmd + ' ' + agent
            if self.args.publisher_auth:
                auth = self.args.publisher_auth
                print('-Enable ' + agent + ' agent authentication: ' + auth + '-')
                logging.info('Enable ' + agent + ' agent authentication: ' + auth)
                cmd = cmd + ' ' + auth
            else:
                print('-Enable ' + agent + ' agent-')
                logging.info('Enable ' + agent + ' agent')
        else:
            cmd = cmd + ' false'
        out = pssh(cmd=cmd, hosts_file=hosts_file, max_threads=max_threads, user=self.args.user)
        logging.info(out)
        print('--------------------------')
        print('-Deploying Complete')

    def deploy_work_docker(self, hosts_file, max_threads=16):
        copy_path = './src/worker/deploy_docker.sh'
        destination_dir = '/tmp/moneo-worker'
        print('-Deploying docker containers to Nvidia support workers)-')
        logging.info('Deploying docker container to workers')
        out = pscp(copy_path, destination_dir, hosts_file, user=self.args.user)
        logging.info(out)
        out = pssh(cmd='/tmp/moneo-worker/deploy_docker.sh',
                   hosts_file=hosts_file, max_threads=max_threads, user=self.args.user)
        logging.info(out)
        print('-Deploying Complete')

    def check_command_result(self, result):
        if 'Permission denied' in result:
            logging.error("SSH permission denied issue with output:{}".format(result))
            raise Exception('SSH permission issue')
        elif 'failure in name resolution' in result:
            logging.error("Host resolution issue with output:{}".format(result))
            raise Exception('Host resolution issue')
        else:
            logging.info(result)

    def deploy_manager(self, work_host_file, user=None, manager_host='localhost', export_AzInsight=False, export_Prometheus=False):
        ssh_host = manager_host
        if user:
            ssh_host = "{}@{}".format(user, manager_host)
        copy_path = "src/master/"
        destination_dir = '/tmp/moneo-master'
        print('-Copying files to manager-')
        logging.info('Copying files to manager')
        ssh_asking = '-o StrictHostKeyChecking=no'
        cmd = "ssh {} {} 'rm -rf {}'".format(ssh_asking, ssh_host, destination_dir)
        self.check_command_result(shell_cmd(cmd, 30))
        cmd = "scp -r {} {}:{}".format(copy_path, ssh_host, '/tmp/')
        self.check_command_result(shell_cmd(cmd, 30))
        cmd = "ssh {} {} 'mv {} {}'".format(ssh_asking, ssh_host, '/tmp/master', destination_dir)
        self.check_command_result(shell_cmd(cmd, 30))
        print('--------------------------')
        print('-Deploying Grafana and Prometheus docker containers to manager-')
        logging.info('Deploying Grafana and Prometheus docker containers to manager')
        cmd = "ssh {} {} 'sudo /tmp/moneo-master/managerLaunch.sh {} {}' \
            ".format(ssh_asking, ssh_host, work_host_file, manager_host)
        self.check_command_result(shell_cmd(cmd, 60))
        print('--------------------------')
        if export_AzInsight:
            print('-Starting Azure insights collector-')
            logging.info('Starting Azure insights collector')
            copy_path = "src/azinsights"
            cmd = "scp {} -r {} {}:{}".format(ssh_asking, copy_path, ssh_host, destination_dir)
            self.check_command_result(shell_cmd(cmd, 30))
            copy_path = "./config.ini"
            cmd = "scp {} -r {} {}:{}//azinsights".format(ssh_asking, copy_path, ssh_host, destination_dir)
            self.check_command_result(shell_cmd(cmd, 30))
            print('--------------------------')
        if export_Prometheus:
            print('-Starting Prometheus sidecar-')
            logging.info('Starting Prometheus sidecar')
            cmd = "ssh {} {} 'sudo /tmp/moneo-master/start_sidecar.sh'".format(ssh_asking, ssh_host)
            self.check_command_result(shell_cmd(cmd, 60))
            print('--------------------------')
        print('-Deploying Complete-')

    def shutdown_worker(self, hosts_file, max_threads=16,):
        cmd = '/tmp/moneo-worker/shutdown.sh true'
        out = pssh(cmd=cmd, hosts_file=hosts_file, max_threads=max_threads, user=self.args.user)
        logging.info(out)

    def shutdown_manager(self, user=None, manager_host='localhost'):
        ssh_host = manager_host
        if user:
            ssh_host = "{}@{}".format(user, manager_host)
        cmd = "ssh {} {} 'sudo /tmp/moneo-master/shutdown.sh'".format("-o StrictHostKeyChecking=no", ssh_host)
        self.check_command_result(shell_cmd(cmd, 60))


def check_deploy_shutdown(args, parser):
    '''
    Checks if the necessary arguments are provided for
    deploy and shutdwon
    '''

    if (not os.path.isfile(args.host_file)):
        print(args.host_file + " does not exist. Please provide a host file. i.e. host.ini.\n")
        parser.print_help()
        exit(1)
    else:
        # ensure we have the absolute path
        args.host_file = os.path.abspath(args.host_file)
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


def parallel_ssh_check():
    """check parallel ssh installed"""

    os_type = shell_cmd('awk -F= \'/^NAME/{print $2}\' /etc/os-release', 45)

    if 'Ubuntu' in os_type:
        pkg_check_results = shell_cmd('dpkg -s pssh', 45)
    else:
        pkg_check_results = shell_cmd('rpm -q pssh', 45)

    if 'not installed' in pkg_check_results:
        logging.error('pssh is not installed, please install pssh to continue')
        print('pssh is not installed.'
              'Moneo CLI requires pssh to distribute commands to the worker nodes. Please install PSSH')
        exit(1)
    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Moneo CLI Help Menu',
        prog='moneo.py',
        usage='%(prog)s [-d ] [-c HOST_FILE] [{manager,workers,full}] \
        \nusage: %(prog)s [-s ] [-c HOST_FILE] [{manager,workers,full}] \
        \nusage: %(prog)s [-j JOB_ID ] [-c HOST_FILE] \
        \ni.e. python3 moneo.py -d -c ./host.ini full'
    )

    parser.add_argument(
        '-c',
        '--host_file',
        default='./hostfile',
        help='Provide filepath and name to hostfile. The default is hostfile in the Moneo directory.')
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
        help='Requires host file to be specified (i.e. -c hostfile) or file to be in Moneo directory.')
    parser.add_argument(
        '-s',
        '--shutdown',
        action='store_true',
        help='Requires host file to be specified (i.e. -c hostfile) or file to be in Moneo directory.')
    parser.add_argument(
        '-i',
        '--insights',
        action='store_true',
        help='Experimental feature: Enable exporting of metrics to Azure Insights. '
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
        help='The number of processes used to deploy/shutdown/update Moneo. '
             'Increasing process count can reduce the latency when deploying to large number of nodes. Default is 16.')
    parser.add_argument(
        '-w',
        '--skip_install',
        action='store_true',
        default=False,
        help='Skip worker software install')
    parser.add_argument(
        '-u',
        '--user',
        default=None,
        help='Provide username to use on remote VMs if not the same as current machine. Default is none')
    parser.add_argument(
        '-m',
        '--manager_host',
        default='localhost',
        help='Manager hostname or IP. Default is localhost.')
    parser.add_argument(
        '-g',
        '--launch_publisher',
        type=str,
        help='This launches the publisher which will share exporter data with Azure. Choices: {geneva, azure_monitor}.')
    parser.add_argument(
        '-a',
        '--publisher_auth',
        type=str,
        help='Required if launching publisher with geneva. Authentication method for geneva. Choices: {umi, cert}. '
             'Please replace the mdm-key.pem and mdm-cert.pem in src/worker/publisher/config with yours if using cert.')
    parser.add_argument(
        '-e',
        '--enable_prometheus',
        action='store_true',
        default=False,
        help='Remote write promethues metrics to azure monitor workspace endpoint. Default is False.')

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, filename='./moneoCLI.log', format='[%(asctime)s] moneoCLI-%(levelname)s-%(message)s')
    try:
        mCLI = MoneoCLI(args)
        #   Workflow selection
        if not parallel_ssh_check():
            exit(1)
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
            if (not os.path.isfile(args.host_file)):
                print(
                    args.host_file + " does not exist. Please provide a host file. i.e. hostfile.\n")
                parser.print_help()
                exit(1)
            mCLI.jobID_update()
        else:
            parser.print_help()
    except Exception as e:
        print('An exception was raised. Please see moneoCLI.log')
        logging.error('Raised exception. Message: %s', e)

    exit(0)
