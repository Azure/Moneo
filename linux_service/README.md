Moneo as a Linux Service
=====
Description
-----
Setting up Moneo exporters as Linux service will allow for easy management and deployment of exporters.
This guide will walk you through how to set up Linux services for Moneo exporters.

Prerequisites
-----
If using [Azure's Ubuntu HPC AI VM image](https://ms.portal.azure.com/#view/Microsoft_Azure_Marketplace/GalleryItemDetailsBladeNopdl/id/microsoft-dsvm.ubuntu-hpc/selectionMode~/false/resourceGroupId//resourceGroupLocation//dontDiscardJourney~/false/selectedMenuId/home/launchingContext~/%7B%22galleryItemId%22%3A%22microsoft-dsvm.ubuntu-hpc2004%22%2C%22source%22%3A%5B%22GalleryFeaturedMenuItemPart%22%2C%22VirtualizedTileDetails%22%5D%2C%22menuItemId%22%3A%22home%22%2C%22subMenuItemId%22%3A%22Search%20results%22%2C%22telemetryId%22%3A%2262513c30-f61d-4cd6-905f-78a3b6869651%22%7D/searchTelemetryId/faaf2f52-2750-4243-b9a1-19f43797cbd3/isLiteSearchFlowEnabled~/false) all dependencies will already be installed. Dependencies can be installed on workers using this script [Install Script](../src/worker/install/install.sh).

Bellow are the dependencies needed (installed by the the install script):
1. Python Packages:
  - prometheus-client==0.16.0
  - psutil==5.9.4
  - filelock==3.10.0
2. DCGM 3.1.6

Configure (only if using experimental publisher service)
-----
To use the geneva or monitor service you must first modify the configuration files.
1. Moneo/src/worker/install/config/geneva_config.json
2. Moneo/src/worker/publisher/config/publisher_config.json

Instructions
-----
1. Install dependencies using install script (not needed if dependencies already installed)
  - ```sudo ../src/worker/install/install.sh true```
2. Run the [configure_service.sh](./configure_service.sh) with the full Moneo path as an argument
  - ```sudo ./configure_service.sh <Moneo_PATH>```
  - If an argument isn't provide it will use the default directory: i.e. /opt/azurehpc/tools/Moneo

Note: The configure script will modify the moneo@.service file to point to the exporter scripts.

3. To start the services run the following commands:
  - With start script:
  ``` sudo ./start_moneo_services.sh```
  - With publisher using start script (experimental, do not use unless advised to):
  ```sudo ./start_moneo_services.sh true```
  - Manually:
  ```
  sudo systemctl start moneo@node_exporter.service
  sudo systemctl start moneo@net_exporter.service
  sudo systemctl start moneo@nvidia_exporter.service
  ```
  - Manually with publisher(experimental, do not use unless advised to):
  ```
  sudo systemctl start moneo@node_exporter.service
  sudo systemctl start moneo@net_exporter.service
  sudo systemctl start moneo@nvidia_exporter.service
  sleep 5
  sudo systemctl start moneo_publisher.service 
  ```
4. To stop the services run:
- With stop script:
  ``` sudo ./stop_moneo_services.sh ```
- Manually:
  ```
  sudo systemctl stop moneo@node_exporter.service
  sudo systemctl stop moneo@net_exporter.service
  sudo systemctl stop moneo@nvidia_exporter.service
  sudo systemctl stop moneo_publisher.service
  ```
5. To run these commands on multiple VMs in parallel you can use a tool like parallel-ssh:
```parallel-ssh -i -t 0 -h hostfile "<command>"```

Updating job ID
-----
To update job name/ID we can use the [job ID update script](../src/worker/jobIdUpdate.sh):

```sudo ../src/worker/jobIdUpdate.sh <jobname/ID>```

Note: use parallel-ssh to distribute this command to a cluster (i.e. step 5 of the instructions)

