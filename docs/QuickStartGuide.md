# Moneo Quick Start Guide #

1. Clone Moneo from Github.

    ```sh
        # get the code
        git clone https://github.com/Azure/Moneo.git
        cd Moneo
        # install dependencies
        sudo apt-get install pssh
    ```

    Note: If you are using an [Azure Ubuntu HPC-AI](https://github.com/Azure/azhpc-images) VM image you can find the Moneo in this path: /opt/azurehpc/tools/Moneo

## Preffered Moneo Deployment ##

The preffered way to deploy Moneo is the headless method using Azure Managaed Grafana and Prometheus resources.

Complete the steps listed here: [Headless Deployment Guide](./HeadlessDeployment.md)

## Alternative deployment using Moneo CLI and head node ##

This method requires a deploying of a head node to host the local Prometheus database and Grafana server.

- The headnode must have enough storage available to facilitate data collection
- Grafana and Prometheus is accessed via web browser. Ensure proper access from web browser to headnode IP.

Complete the steps listed here: [Local Grafana Deployment Guide](./HeadlessDeployment.md)

## Known Issues ##

- NVIDIA exporter may conflict with DCGMI

  There're [two modes for DCGM](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#content): embedded mode and standalone mode.

  If DCGM is started as embedded mode (e.g., `nv-hostengine -n`, using no daemon option `-n`), the exporter will use the DCGM agent while DCGMI may return error.

  It's recommended to start DCGM in standalone mode in a daemon, so that multiple clients like exporter and DCGMI can interact with DCGM at the same time, according to [NVIDIA](https://docs.nvidia.com/datacenter/dcgm/latest/dcgm-user-guide/getting-started.html#standalone-mode).

  > Generally, NVIDIA prefers this mode of operation, as it provides the most flexibility and lowest maintenance cost to users.

- Moneo will attempt to install a tested version of DCGM if it is not present on the worker nodes. However, this step is skipped if DCGM is already installed. In instances DCGM installed may be too old.

  This may cause the Nvidia exporter to fail. In this case it is recommended that DCGM be upgrade to atleast version 2.4.4.
  To view which exporters are running on a worker just run ```ps -eaf | grep python3```

## Troubleshooting ##

1.
2. For deployments with a Headnode:

    - Verifying Grafana and Prometheus containers are running:
        - Check browser http://master-ip-or-domain:3000 (Grafana), http://master-ip-or-domain:9090 (Prometheus)
        - On Manager node terminal run ```sudo docker container ls```
    ![image](https://user-images.githubusercontent.com/70273488/205715440-9f994c84-b115-4a98-9535-fdce8a4adf7d.png)

3. All deployments:
    - Verifying exporters on worker node:
        - ``` ps -eaf | grep python3 ```

    ![image](https://user-images.githubusercontent.com/70273488/205716391-d0144085-8948-4269-a25c-51bc68448e1e.png)
