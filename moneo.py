# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import os

def deploy(args):
    dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/deploy.yaml'
    
    if args.deploy == 'workers':
        dep_cmd= dep_cmd + ' -e "skip_master=true"'
    if args.deploy == 'master' :
        dep_cmd= dep_cmd + ' -e "skip_worker=true"'
    
    print('Deployment type: ' + args.deploy)
    os.system(dep_cmd)
    
def stop(args):
    while(True) :
        confirm = input("Are you sure you would like to stop Moneo? (Y/n)\n")
        
        if confirm.upper() == 'Y' :    
            dep_cmd='ansible-playbook -i ' + args.host_ini + ' src/ansible/shutdown.yaml'
            if args.shutdown=='workers':
                dep_cmd= dep_cmd + ' -e "skip_master=true"'
            if args.shutdown == 'manager':
                dep_cmd= dep_cmd + ' -e "skip_worker=true"'
            os.system(dep_cmd)
            print("Moneo is Shutting down \n")
            return 0
        
        elif confirm.upper() == 'N':
            print("Canceling request to shutdown Moneo \n")
            return 0
        else:
            print("Input not recognized\n")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Moneo CLI',prog='moneo.py',usage='%(prog)s [-d {manager,workers,full}] [-c HOST_INI] \nusage: %(prog)s [-s {manager,workers,full}] [-c HOST_INI]')  
    parser.add_argument('-d','--deploy' ,choices=['manager', 'workers', 'full'],help=' Deployment choices: {manager,workers,full}. Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument('-s','--shutdown',choices=['manager', 'workers', 'full'], help='Shutdown choices: {manager,workers,full}.  Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.')
    parser.add_argument('-c','--host_ini',default='./host.ini', help='Provide filepath and name of ansible config file. The default is host.ini in the Moneo directory.' )    
    args = parser.parse_args()
    
    if(args.deploy and args.shutdown):
         print("deploy and shutdown are exclusive arguments. Please only provide one.")
         parser.print_help()
         exit(1)
    elif(args.deploy):
        if (not os.path.isfile(args.host_ini)) :
            print(args.host_ini + " does not exist. Please provide a a host file. i.e. host.ini.")
            parser.print_help()
            exit(1)
        deploy(args)
    elif(args.shutdown):
        if (not os.path.isfile(args.host_ini)) :
            print(args.host_ini + " does not exist. Please provide a host file. i.e. host.ini.")
            parser.print_help()
            exit(1)    
        stop(args)
    else:
        parser.print_help()

    exit(0)
