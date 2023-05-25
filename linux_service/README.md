Moneo as a Linux Service
=====
Description
-----
Setting up Moneo exporters as Linux service will allow for easy management and deployment of exporters.


Three launch methods provided:
1. The basic launch method launches the exporters on the compute node. It is up to the user to either:
   - Use Moneo CLI to launch the manager Grafana and Prometheus containers on a head node.
   - Or use you own method to scrape from the exporter ports ("nvidia_exporter": 8000 "net_exporter": 8001 "node_exporter": 8002).
2. Launch exporters and an [Azure Monitor](../docs/AzureMonitorAgent.md) publisher.
   - Before launch you must modify the "azure_monitor_agent_config" section of [publisher_config](../src/worker/publisher/config/publisher_config.json) file with the Azure monitor workspace connection string.
3. Azure Managed Grafana/Prometheus.
   - This will require you to set up Managed Prometheus and Managed Grafana
   - See prereqs for [Managed Prometheus](../docs/ManagedPrometheusAgent.md)
   - Once Managed Prometheus is set up you can link it to a Grafana Dashboard.
   - See [Azure Managed Grafana overview](https://learn.microsoft.com/en-us/azure/managed-grafana/overview) for info on setting up Grafana.

This guide will walk you through how to set up Linux services for Moneo exporters.

Prerequisites
-----
If using [Azure's Ubuntu HPC AI VM image](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/microsoft-dsvm.ubuntu-hpc?tab=overview) all dependencies will already be installed. Additional dependencies are installed as part of this guide. Please see [Install Script](../src/worker/install/install.sh) for details on what Python and Ubuntu packages are installed. DCGM 3.1.6 and higher is required for GPU nodes. This will also be checked/installed via the instll script as part of this guide.

Bellow are the prereqs needed:
- PSSH (This can be interchanged with other tools that can do distributed commands. The instructions will use PSSH for Ubuntu)
- AlmaLinux 8.7
- Ubuntu 20.04/22.04
- Moneo cloned/installed in the same directory on all compute nodes.
- A hostfile with the target compute nodes.
 

Instructions for Configuring, Installing and Launching Moneo services
-----
### Configuration and Instalation ###
1. Configuration and installation of the Linux service is done with the following command:
   ```parallel-ssh -i -t 0 -h hostfile "sudo <Full Path to Moneo>/linux_service/configure_service.sh <Full Path to Moneo>"```
   - If You will only be launching the exporters without AZ monitor or Managed Prometheus Continue to the Launch Services section else continue.
2. For Azure Monitor or Managaed Prometheus methods if you have not yet modified the configuration files reference the following:
   - For Azure Managed Prometheus:
     - modify [prom_sidecar_config.json](../src/worker/publisher/config) and copy the file to the compute nodes.
     - ```parallel-scp -h hostfile <Full Path to Moneo>/src/worker/publisher/config/prom_sidecar_config.json  <Full Path to Moneo>/src/worker/publisher/config```
     - Lastly check that that the managed user identity used to set up Managed Prometheus (Azure role assignments) is assigned to your VMSS.
   - For Azure Monitor:
      -  modify the connection string of "azure_monitor_agent_config" section and copy the file to the compute nodes.
      -  ```parallel-scp -h hostfile <Full Path to Moneo>/src/worker/publisher/config/publisher_config.json <Full Path to Moneo>/src/worker/publisher/config```
   
### Launch Services ###
#### Exportesr only Launch ####
```parallel-ssh -i -t 0 -h hostfile "sudo <Full Path to Moneo>/linux_service/start_moneo_services.sh <Full Path to Moneo> false false"```
#### Exporters with Azure Monitor ####
```parallel-ssh -i -t 0 -h hostfile "sudo <Full Path to Moneo>/linux_service/start_moneo_services.sh <Full Path to Moneo> false true"```
#### Exporters with Managed Prometheus ####
```parallel-ssh -i -t 0 -h hostfile "sudo <Full Path to Moneo>/linux_service/start_moneo_services.sh <Full Path to Moneo> true false"```

Updating job ID
-----
To update job name/ID we can use the [job ID update script](../src/worker/jobIdUpdate.sh):

```sudo ../src/worker/jobIdUpdate.sh <jobname/ID>```

or see [Update Job Id With Moneo CLI](../docs/JobFiltering.md)

Note: use parallel-ssh to distribute this command to a cluster (i.e. step 5 of the instructions)

