Moneo as a Linux Service
=====
Description
-----
Setting up Moneo exporters as Linux service will allow for easy management and deployment of exporters.
This guide will walk you through how to set up Linux services for Moneo exporters.

Prerequisites
-----
If using [Azure's Ubuntu HPC AI VM image](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/microsoft-dsvm.ubuntu-hpc?tab=overview) all dependencies will already be installed. Dependencies can be installed on workers using this script [Install Script](../src/worker/install/install.sh).

Bellow are the dependencies needed (installed by the the install script):
1. Python Packages:
  - prometheus-client==0.16.0
  - psutil==5.9.4
  - filelock==3.10.0
2. DCGM 3.1.6

Instructions without Publisher service
-----
1. Install dependencies using install script (not needed if dependencies already installed)
   - ```sudo ../src/worker/install/install.sh```

2. Run the [configure_service.sh](./configure_service.sh) with the full Moneo path as an argument
   - ```sudo ./configure_service.sh <Moneo_PATH>```
   - If an argument isn't provide it will use the default directory: i.e. /opt/azurehpc/tools/Moneo

Note: The configure script will modify the moneo@.service file to point to the exporter scripts.

3. To start the services run the following commands:
   - With start script:
  ``` sudo ./start_moneo_services.sh```
   - Manually:
  ```
  sudo systemctl start moneo@node_exporter.service
  sudo systemctl start moneo@net_exporter.service
  sudo systemctl start moneo@nvidia_exporter.service
  ```
4. To stop the services run:
   - With stop script:
  ``` sudo ./stop_moneo_services.sh ```
   - Manually:
  ```
  sudo systemctl stop moneo@node_exporter.service
  sudo systemctl stop moneo@net_exporter.service
  sudo systemctl stop moneo@nvidia_exporter.service
  ```
5. To run these commands on multiple VMs in parallel you can use a tool like parallel-ssh:
   - ```parallel-ssh -i -t 0 -h hostfile "<command>"```

Instructions for Moneo services with Publisher service
-----
The publisher service is experimental and requires additional setup to use.
1. Modify publisher config files
   - Moneo/src/worker/install/config/geneva_config.json
   - Moneo/src/worker/publisher/config/publisher_config.json

2. Install dependencies using install script (not needed if dependencies already installed)
   - Include Geneva agent install: ```sudo ../src/worker/install/install.sh geneva```
   - Include Azure monitor install: ```sudo ../src/worker/install/install.sh azure_monitor```

3. Run the [configure_service.sh](./configure_service.sh) with the full Moneo path as an argument
   - ```sudo ./configure_service.sh <Moneo_PATH> <publisher type>```
   - Publisher types: "geneva" and "azure_monitor"

4. To start the services run the following commands based on the publisher type:
   - ```sudo ./start_moneo_services.sh geneva <moneo path>```
   - ```sudo ./start_moneo_services.sh azure_monitor```
5. To stop the services run:
   - ```sudo ./stop_moneo_services.sh ```
6. To run these commands on multiple VMs in parallel you can use a tool like parallel-ssh:
   - ```parallel-ssh -i -t 0 -h hostfile "<command>"```


Updating job ID
-----
To update job name/ID we can use the [job ID update script](../src/worker/jobIdUpdate.sh):

```sudo ../src/worker/jobIdUpdate.sh <jobname/ID>```

Note: use parallel-ssh to distribute this command to a cluster (i.e. step 5 of the instructions)

