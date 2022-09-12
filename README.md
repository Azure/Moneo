Moneo
=====
Description
-----
Moneo is a distributed GPU system monitor for AI workflows.

Moneo orchestrates metric collection (DCGMI + Prometheus DB) and visualization (Grafana) across multi-GPU/node systems. This provides useful insights into workflow and system level characterization.
<details>
<summary>Metrics</summary>

There three categories of metrics that Moneo monitors:
1.	GPU Counters
    - Compute/Memory Utilization
    - SM and Memory Clock frequency
    - Temperature
    - Power
    - ECC Counts
    - GPU Throttling
2.	GPU Profiling Counters
    - SM Activity
    - Memory Dram Activity
    - NVLink Activity
    - PCIE Rate
3.	InfiniBand Network Counters
    - IB TX/RX rate
    - IB Port errors
</details>

<details>
<summary>Grafana Dashboards</summary>

1. Menu: List of available dashboards.
![image](https://user-images.githubusercontent.com/70273488/186491552-34d545de-b60d-4cdd-aed4-702e2f34d974.png)

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
</details>

Minimum Requirements
-----

- python >=3.7 installed
- docker installed
- ansible installed

Setup
-----

Run following commands on dev box (could be one of the master/worker nodes or a local node):

```sh
# get the code
git clone https://github.com/Azure/Moneo.git
cd Moneo

# install dependencies
python3 -m pip install ansible
```

Configuration
-------------

Prepare a config file `host.ini` for all master/worker nodes, here's an example:

```ini
[master]
192.168.0.100

[worker]
192.168.0.100
192.168.0.101
192.168.0.110

[all:vars]
ansible_user=username
ansible_ssh_private_key_file=/path/to/key
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

If you have configured passwordless SSH already, `[all:vars]` section can be skipped.

Please refer to [Ansible Inventory docs](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) for more complex cases.

Usage
-----
### _Moneo CLI_
To make deploying and shutting down easier we provide the Moneo CLI. 

Which can be accessed as such:

*   ```sh
    python3 moneo.py --help
    ```
#### CLI Usage
* ```python3 moneo.py [-d/--deploy] [-c HOST_INI] {manager,workers,full}```
* ```python3 moneo.py [-s/--shutdown] [-c HOST_INI] {manager,workers,full}```
* ```python3 moneo.py [-j JOB_ID ] [-c HOST_INI]```
* i.e. ```python3 moneo.py -d -c ./host.ini full```


| Flag                           | Options/arguments        |Description|
|--------------------------------|--------------------------|--------|
|-d, --deploy | None   |Deploy option selection. Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.|
|-s, --shutdown| None  |Shutdown option selection. Requires config file to be specified (i.e. -c host.ini) or file to be in Moneo directory.|
|-c, --host_ini    | path + file name    |Provide filepath and name of ansible config file. The default is host.ini in the Moneo directory.|
|-j , --job_id | Job ID |Job ID for filtering metrics by job group. Host.ini file required. Cannot be specified during deployment and shutdown.|
|-p, --profiler_metrics | None|Enable profile metrics (Tensor Core,FP16,FP32,FP64 activity). Addition of profile metrics encurs additional overhead on computer nodes.|
| | {manager,workers,full} | Type of deployment/shutdown. Choices: {manager,workers,full}. Default: full. |

### _Access the Portal_

The Prometheus and Grafana services will be started on master nodes after deployment.
You can access the Grafana portal to visualize collected metrics.

There are several cases based on the networking configuration:

* If the master node has a public IP address or domain, you can access the portal through `http://master-ip-or-domain:3000` directly.

  For example, if you are deploying for Azure VM or VMSS, you can [associate a public IP address](https://docs.microsoft.com/en-us/azure/virtual-network/ip-services/associate-public-ip-address-vm) to the master node, then create a [fully qualified domain name (FQDN)](https://docs.microsoft.com/en-us/azure/virtual-machines/create-fqdn) for it.

* If the master node does not have a public IP address to access, e.g., the VMSS is created behind a load balancer, you will need to create a proxy to access.

  For example, you can create a socks5 proxy at `socks5://localhost:1080` through `ssh -D 1080 -p PORT USER@IP`, then install [Proxy SwitchyOmega](https://chrome.google.com/webstore/detail/proxy-switchyomega/padekgcemlokbadohgkifijomclgjgif?hl=en) in Edge/Chrome browser and configure the proxy to protocol `socks5`, server `localhost`, port `1080` for all schemes, you will be able to navigate portal using master node's hostname at `http://master-hostname:3000`.

* Default Grafana access:
    *  username: azure
    *  password: azure
    
  This can be changed in the "src/master/grafana/grafana.env" file.

### _Quick Start Guide_ ###

[Quick Start](./docs/QuickStartGuide.md)

### _Job Level Filtering_ ###
Moneo provides a way to filter nodes by job group. To get started with job level filtering see:
[Job Level Filtering](./docs/JobFiltering.md)

### _Azure Application Insights for Metric Visualization_ ###
[Azure Application Insights for Metric Visualization](src/azinsights/README.md)

Known Issues
------------

* NVIDIA exporter may conflict with DCGMI

  There're [two modes for DCGM](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#content): embedded mode and standalone mode.

  If DCGM is started as embedded mode (e.g., `nv-hostengine -n`, using no daemon option `-n`), the exporter will use the DCGM agent while DCGMI may return error.

  It's recommended to start DCGM in standalone mode in a daemon, so that multiple clients like exporter and DCGMI can interact with DCGM at the same time, according to [NVIDIA](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#standalone-mode).

  > Generally, NVIDIA prefers this mode of operation, as it provides the most flexibility and lowest maintenance cost to users.


## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
