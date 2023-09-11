# Moneo #

## Description ##

Moneo is a distributed GPU system monitor for AI workflows.

Moneo orchestrates metric collection (DCGMI + Prometheus DB) and visualization (Grafana) across multi-GPU/node systems. This provides useful insights into workflow and system level characterization.
<details>
<summary>Metrics</summary>

There five categories of metrics that Moneo monitors:

1. GPU Counters

    - Compute/Memory Utilization
    - SM and Memory Clock frequency
    - Temperature
    - Power
    - ECC Counts (Nvidia)
    - GPU Throttling (Nvidia)
    - XID code (Nvidia)
2. GPU Profiling Counters
    - SM Activity
    - Memory Dram Activity
    - NVLink Activity
    - PCIE Rate
3. InfiniBand Network Counters
    - IB TX/RX rate
    - IB Port errors
    - IB Link FLap
4. CPU Counters
    - Utilization
    - Clock frequency
5. Memory
    - Utilization

</details>

<details>
<summary>Grafana Dashboards</summary>

1. Menu: List of available dashboards.
![image](https://user-images.githubusercontent.com/107515145/195170743-0b4755b5-f97f-4a00-883f-0560400620f9.png)

   Note: When viewing GPU dashboards make sure to note whether you are using Nvidia or AMD GPU nodes and select the proper dashboard.

2. Cluster View: contains  min, max, average across devices for GPU/IB metrics per VM.
![image](https://user-images.githubusercontent.com/70273488/186491238-ce032f87-cab1-41c4-b32e-9826b8c47b72.png)
![image](https://user-images.githubusercontent.com/70273488/186491363-3a6cdb8d-0d95-4deb-a6b0-e28711f1ba56.png)

3. GPU Device Counters: Detailed view of node level GPU counters.
![image](https://user-images.githubusercontent.com/70273488/173664219-43d8d7b7-a4e6-440a-8373-89ca388ce563.png)

4. GPU Profiling Counters: Node level profiling metrics require additional overhead which may affect workload performance. Tensor, FP16, FP32, and FP64 activity are disabled by default but can be switched on by CLI command.
![image](https://user-images.githubusercontent.com/70273488/173661651-2aa3d586-3889-45f9-81e7-c8140fb19405.png)

5. InfiniBand Network Counters: Detailed view of node level IB network metrics.
![image](https://user-images.githubusercontent.com/70273488/173664809-bbfea8b4-91cb-42cd-aff8-a91fc9006120.png)

6. Node View: Detailed view of node level CPU, Memory, and Network metrics.
![image](https://user-images.githubusercontent.com/107515145/195173202-8812a46a-4334-4e52-87ba-3c3137711bdd.png)

</details>

## Minimum Requirements ##

-----

- python >=3.7 installed

- OS Support:
  - Ubuntu 18.04, 20.04, 22.04
  - AlmaLinux 8.6

### Manager node requirements ###

Note: Not applicable if using Azure Managed Grafana/Prometheus

- docker 20.10.23 (May work with other versions but this has been tested.)
- parallel-ssh 2.3.1-2 (May work with other versions but this has been tested.)
- Manager node must be able to ssh to itself

### Worker node requirements ###

- Nvidia Architecture supported (only for Nvidai GPU monitoring):
  - Volta
  - Ampere
  - Hopper
- docker 20.10.23 (Only if using geneva agent. May work with other versions but this has been tested.)
- Installed with install script at time of deployment (If not installed.):
  - DCGM 3.1.6
  - pip3
  - prometheus_client
  - psutil
  - filelock

## Usage ##

-----

### Deploying Moneo ###

There are a few methods to deploy Moneo. They can be found here [Getting started Guide](./docs/QuickStartGuide.md)

1. Preffered Method Using Azure Managed Prometheus/Grafana and Moneo linux services for collection
2. Alternative 1: Using Azure Monitor Workspace and Moneo linux services for collection
3. Alternative 2: Using Moneo CLI with a dedicate headnode to host local Prometheus/Grafana servers

Note: Moneo CLI can be used in place of Moneo linux services to deploy Moneo workers

### Moneo CLI ###

Moneo CLI provides an alternative way to deploy and update Moneo manager and worker nodes. Although linux services are preffered this offeres an alternative way to control Moneo.

#### CLI Usage ####

- ```python3 moneo.py [-d/--deploy] [-c hostfile] {manager,workers,full}```
- ```python3 moneo.py [-s/--shutdown] [-c hostfile] {manager,workers,full}```
- ```python3 moneo.py [-j JOB_ID ] [-c hostfile]```
- i.e. ```python3 moneo.py -d -c ./hostfile full```

Note: For more options check the Moneo help menu

```sh
python3 moneo.py --help
```

### Access the Grafana Portal ###

- For Azure Managed Grafana the dashboards can be accessed via the endpoint provided on the resource overview.
- For Moneo CLI deployment with a dedicated head node the Grafana portal can be reached via browser: http://master-ip-or-domain:3000
- If Azure Monitor is used instead of Managed or local Grafana then you can navigate to the Azure Monitor Workspace on The Azure portal.
  
### _User Docs_ ###

- [Quick Start](./docs/QuickStartGuide.md)
- To get started with job level filtering see: [Job Level Filtering](./docs/JobFiltering.md)
- Slurm epilog/prolog integration: [Slurm example](./examples/slurm/README.md)
- To deploy moneo-worker inside container: [Moneo-exporter](./docs/Moneo-exporter.md)
- To integrate Moneo with Azure Insights dashboard see: [Azure Monitor](./docs/AzureMonitorAgent.md)

### Known Issues ###

-----

- NVIDIA exporter may conflict with DCGMI

  There're [two modes for DCGM](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#content): embedded mode and standalone mode.

  If DCGM is started as embedded mode (e.g., `nv-hostengine -n`, using no daemon option `-n`), the exporter will use the DCGM agent while DCGMI may return error.

  It's recommended to start DCGM in standalone mode in a daemon, so that multiple clients like exporter and DCGMI can interact with DCGM at the same time, according to [NVIDIA](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#standalone-mode).

  > Generally, NVIDIA prefers this mode of operation, as it provides the most flexibility and lowest maintenance cost to users.

- Moneo will attempt to install a tested version of DCGM if it is not present on the worker nodes. However, this step is skipped if DCGM is already installed. In instances DCGM installed may be too old.

  This may cause the Nvidia exporter to fail. In this case it is recommended that DCGM be upgrade to atleast version 2.4.4.
  To view which exporters are running on a worker just run ```ps -eaf | grep python3```

## Troubleshooting ##

-----

- Verifying Grafana and Prometheus containers are running:
  - Check browser http://master-ip-or-domain:3000 (Grafana), http://master-ip-or-domain:9090 (Prometheus)
  - On Manager node terminal run ```sudo docker container ls```
  
    ![image](https://user-images.githubusercontent.com/70273488/205715440-9f994c84-b115-4a98-9535-fdce8a4adf7d.png)
- Verifying exporters on worker node:
  - ``` ps -eaf | grep python3 ```

    ![image](https://user-images.githubusercontent.com/70273488/205716391-d0144085-8948-4269-a25c-51bc68448e1e.png)

## Contributing ##

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks ##

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
