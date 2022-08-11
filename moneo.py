# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import os

def deploy(args):
    '''Deploys Moneo monitoring to hosts listed in the specified host ini file'''
    dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/deploy.yaml'
    
    if args.type == 'workers':
        dep_cmd= dep_cmd + ' -e "skip_master=true"'
    elif args.type == 'master' :
        dep_cmd= dep_cmd + ' -e "skip_worker=true"'
    
    dep_cmd= dep_cmd + ' -e "skip_insights=' + ('false' if args.insights else 'true') + '"'

    print('Deployment type: ' + args.type)
    os.system(dep_cmd)
    
def stop(args):
    '''Stops Moneo monitoring on hosts listed in the specified host ini file'''
    while(True) :
        confirm = input("Are you sure you would like to perform a '"+ args.type +"' shutdown of Moneo? (Y/n)\n")
        
        if confirm.upper() == 'Y' :    
            dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/shutdown.yaml'
            if args.type=='workers':
                dep_cmd= dep_cmd + ' -e "skip_master=true"'
            elif args.type == 'manager':
                dep_cmd= dep_cmd + ' -e "skip_worker=true"'
            os.system(dep_cmd)
            print("Moneo is Shutting down \n")
            return 0
        
        elif confirm.upper() == 'N':
            print("Canceling request to shutdown Moneo \n")
            return 0
        else:
            print("Input not recognized\n")

def jobID_update(args):
    '''Updates job id for hosts listed in the specified host ini file'''
    dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/updateJobID.yaml -e job_Id=' + args.job_id
        
    print('Job ID update to ' + args.job_id)
    os.system(dep_cmd)

def check_deploy_shutdown(args,parser):
    '''Checks if the necessary arguments are provided for deploy and shutdwon'''
    if (not os.path.isfile(args.host_ini)) :
        print(args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.\n")
        parser.print_help()
        exit(1)
    if(args.job_id):
        print("Job Id cannot be specified during deployment and shutdown. Ignoring Job Id.\n")
    choices=['manager', 'workers', 'full']
    if(args.type[0] not in choices):
        print('Deployment/shutdown type not recognized or entered defaulted to the full option.\n')
        args.type = 'full'
    args.type = args.type[0]

def check_insights_config(args, parser):
    if (args.insights and not os.path.isfile('config.ini')):
        print('The Application Insights configuration file (config.ini) does not exist. Please provide one to use this feature.')
        parser.print_helper()
        exit(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Moneo CLI',prog='moneo.py',usage='%(prog)s [-d ] [-c HOST_INI] [{manager,workers,full}] \
    \nusage: %(prog)s [-s ] [-c HOST_INI] [{manager,workers,full}] \
    \nusage: %(prog)s [-j JOB_ID ] [-c HOST_INI] \
    \ni.e. python3 moneo.py -d -c ./host.ini full')  

    parser.add_argument('-c','--host_ini',default='./host.ini', help='Provide filepath and name of ansible config file. The default is host.ini in the Moneo directory.' )    
    parser.add_argument('-j','--job_id',type=str, help='Job ID for filtering metrics by job group. Host.ini file required. Cannot be specified during deployment and shutdown' )
    parser.add_argument('-d','--deploy', action='store_true',help='Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument('-s','--shutdown',action='store_true', help='Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument('-i', '--insights',action='store_true', help='Enable exporting of metrics to Azure Insights. Requires a valid instrumentation key and base_url for the Prometheus DB in config.ini')
    parser.add_argument('type', metavar='type', type=str,default=['full'], nargs="*", help='Type of deployment/shutdown. Choices: {manager,workers,full}. Default: full.')    

    args = parser.parse_args()
    
    if(args.deploy and args.shutdown):
        print("deploy and shutdown are exclusive arguments. Please only provide one.\n")
        parser.print_help()
        exit(1)
    elif(args.deploy):
        check_deploy_shutdown(args,parser)
        check_insights_config(args,parser)
        deploy(args)
    elif(args.shutdown):  
        check_deploy_shutdown(args,parser)
        stop(args)
    elif(args.job_id):
        if (not os.path.isfile(args.host_ini)) :
            print(args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.\n")
            parser.print_help()
            exit(1)
        jobID_update(args)
    else:
        parser.print_help()

    exit(0)
