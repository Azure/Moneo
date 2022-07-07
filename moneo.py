# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import os

def deploy(args):
    dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/deploy.yaml'
    if args.skip_install :
        dep_cmd= dep_cmd + ' -e "skip_worker=true"'
    dep_cmd= dep_cmd + ' -e "job_Id=' + str(args.job_id) + '"'
    print(dep_cmd)
    os.system(dep_cmd)
    
def stop(args):
    while(True) :
        confirm = input("Are you sure you would like to stop Moneo? (Y/n)\n")
        if confirm.upper() == 'Y' :    
            dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/shutdown.yaml'
            os.system(dep_cmd)
            print("Moneo is Shutting down \n")
            return 0
        elif confirm.upper() == 'N':
            print("Canceling request to shutdown Moneo \n")
            return 0
        else:
            print("Input not recognized\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--deploy',action='store_true',help='Deploy Moneo. This command requires a config file be provided using --host_ini/-c option to specify file. If one is not provided it will attempt to use "host.ini" file in the Moneo directory by default. Moneo will fail to deploy if a file is not present.')
    parser.add_argument('-s','--shutdown',action='store_true', help='Shutdown Moneo. This command requires a config file be provided using --host_ini/-c option to specify file. If one is not provided it will attempt to use "host.ini" file in the Moneo directory by default. Moneo will fail to shutdown if a file is not present.')
    parser.add_argument('-c','--host_ini',default='./host.ini', help='Provide filepath and name of ansible config file. The default is host.ini in the Moneo directory.' )
    parser.add_argument('-j','--job_id',default=-999, help='Job ID for filtering metrics by job group.' )
    parser.add_argument('-k','--skip_install',action='store_true',help='skips instalation of Moneo software on the workers during deployment time')
    args = parser.parse_args()
    
    if(args.deploy and args.shutdown):
        print("deploy and shutdown are exclusive arguments. Please only provide one.")
        exit(1)
    elif(args.deploy):
        if (not os.path.isfile(args.host_ini)) :
            print(args.host_ini + " does not exist. Please provide a a host file. i.e. host.ini.")
            exit(1)
        deploy(args)
    elif(args.shutdown):
        if (not os.path.isfile(args.host_ini)) :
            print(args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.")
            exit(1)    
        stop(args)

    exit(0)