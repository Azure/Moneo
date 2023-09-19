# Moneo as a Linux Service #

## Description ##

-----
Setting up Moneo exporters as Linux service will allow for easy management and deployment of exporters.

Three launch methods provided:

1. Azure Managed Grafana/Prometheus.
   - This will require you to set up Managed Prometheus and Managed Grafana
   - See prereqs for [Managed Prometheus](../docs/ManagedPrometheusAgent.md)
   - Once Managed Prometheus is set up you can link it to a Grafana Dashboard.
   - See [Azure Managed Grafana overview](https://learn.microsoft.com/en-us/azure/managed-grafana/overview) for info on setting up Grafana.
2. The basic launch method launches the exporters on the compute node. It is up to the user to either:
   - Use Moneo CLI to launch the manager Grafana and Prometheus containers on a head node.
   - Or use you own method to scrape from the exporter ports ("nvidia_exporter": 8000 "net_exporter": 8001 "node_exporter": 8002).
3. Launch exporters and an [Azure Monitor](../docs/AzureMonitorAgent.md) publisher.
   - Before launch you must modify the "azure_monitor_agent_config" section of [publisher_config](../src/worker/publisher/config/publisher_config.json) file with the Azure Monitor workspace connection string.

There is one additional method for internal Msft use that exports to Geneva. This method is similar to Azure Monitor method but uses a Geneva agent container to export. Reference the [Moneo Geneva Docs](../docs/GenevaAgent.MD). Ensure all prequisites are met. 

This guide will walk you through how to set up Linux services for Moneo exporters.

## Prerequisites ##

-----
If using [Azure's Ubuntu HPC AI VM image](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/microsoft-dsvm.ubuntu-hpc?tab=overview) all dependencies will already be installed. Additional dependencies are installed as part of this guide. Please see [Install Script](../src/worker/install/install.sh) for details on what Python and Ubuntu packages are installed. DCGM 3.1.6 and higher is required for GPU nodes. This will also be checked/installed via the install script as part of this guide.

Below are the prereqs needed:

- PSSH (This can be interchanged with other tools that can do distributed commands. The instructions will use PSSH for Ubuntu)
- AlmaLinux 8.7
- Ubuntu 20.04/22.04
- Moneo cloned/installed in the same directory on all compute nodes.
- A host file with the target compute nodes.

## Instructions for Configuring, Installing and Launching Moneo services ##

-----

### Configuration and Installation ###

Configuration/Installation is only required once. After that is complete the Linux services can be started and stopped as desired.

1. Configuration and installation of the Linux service is done with the following command:
   ```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/configure_service.sh"```
     - Note: If using Azure monitor or Geneva add an extra argument "./start_moneo_services.sh azure_monitor"  or "./configure_service.sh geneva" respectively.
     - Note: Geneva authentication is user managed identity "umi"by default, you can choose to change to "cert" method by modifiying [the start script](./configure_service.sh) "PUBLISHER_AUTH" variable.

2. For Azure Monitor or Managed Prometheus methods if you have not yet modified the configuration files reference the following:
   - For Azure Managed Prometheus:
     - modify [managed_prom_config.json](../src/worker/publisher/config) and copy the file to the compute nodes.
     - ```parallel-scp -h hostfile /opt/azurehpc/tools/Moneo/src/worker/publisher/config/managed_prom_config.json /opt/azurehpc/tools/Moneo/src/worker/publisher/config```
     - Lastly check that that the managed user identity used to set up Managed Prometheus (Azure role assignments) is assigned to your VMSS.
   - For Azure Monitor:
     - modify the connection string of "azure_monitor_agent_config" section and copy the file to the compute nodes.
     - ```parallel-scp -h hostfile /opt/azurehpc/tools/Moneo/src/worker/publisher/config/publisher_config.json /opt/azurehpc/tools/Moneo/src/worker/publisher/config```

### Launch Services ###

The [start_moneo_services.sh](./start_moneo_services.sh) script is used to start the Linux services once configuration/installation is complete.

#### Exporters with Azure Monitor or Geneva(internal Msft) ####

```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/start_moneo_services.sh azure_monitor"```
   or
```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/start_moneo_services.sh geneva"```

#### Exporters with Managed Prometheus ####

```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/start_moneo_services.sh"```

### Stop Services ###

Stopping services is the same command for all methods.
```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/stop_moneo_services.sh"```

### Recap ###

Assuming configuration files have been updated and user managed ID applied if necessary (Managed Prometheus) reference these commands for the work flow:

- Configuration/Install:
   ```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/configure_service.sh"```
- Extra Configure step for AZ Monitor and/or Managed Prometheus
   ```parallel-scp -h hostfile /opt/azurehpc/tools/Moneo/src/worker/publisher/config/<Respective config file> /opt/azurehpc/tools/Moneo/src/worker/publisher/config```
- Start
   ```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/start_moneo_services.sh"```
   Note:
- Stop
   ```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/stop_moneo_services.sh"```

 Note: This guide uses PSSH to distribute the commands. Any tool that is similar to PSSH can be used such as PDSH. The scipts can also be called from job schedulers or individually.

## Updating job ID ##

-----
To update job name/ID we can use the [job ID update script](../src/worker/jobIdUpdate.sh):

```sudo ../src/worker/jobIdUpdate.sh <jobname/ID>```

or see [Update Job Id With Moneo CLI](../docs/JobFiltering.md)

Note: use parallel-ssh to distribute this command to a cluster
