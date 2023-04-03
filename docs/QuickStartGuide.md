Moneo Quick Start Guide
=====
Description
-----
This guide will walk you through the simple steps of setting up Moneo.
This guide assume that all dependencies and requirements have been meant.

Steps
-----
1. Clone Moneo from Github and install ansible. 
    ```sh
    # get the code
    git clone https://github.com/Azure/Moneo.git
    cd Moneo

    # install dependencies
    sudo apt-get install pssh
    ```
    Note: If you are using an [Azure Ubuntu HPC-AI](https://github.com/Azure/azhpc-images) VM image you can find the Moneo in this path: /opt/azurehpc/tools/Moneo

2. Next create a hostfile file.  
    ```hostfile
    192.168.0.100
    192.168.0.101
    192.168.0.110
    ```
    Note: The manager node can also be a work node as well. The manager node will have the Grafana and Prometheus docker containers deployed to it.
    
    Note: You must have passwordless ssh enabled on your nodes
    
    Note: The manager node must be able to ssh into itself
    
3. Now deploy Moneo
    * using Moneo cli:
    ```sh 
    python3 moneo.py --deploy -c hostfile full
    ```
    * If using the Azure HPC/AI market place image or if installation has been performed on all worker nodes by a previous deploymeny we can skip the install step:
    ```sh 
    python3 moneo.py --deploy -c hostfile full -w
    ```
    Note: See usage section of the README doc for more advance details on Moneo CLI

    Note: By default Moneo deploys to the manager using localhost. This can be changed using the "manager_host" flag.

4. Log into the portal by navigating to `http://manager-ip-or-domain:3000` and inputting your credentials

    ![image](https://user-images.githubusercontent.com/70273488/173685955-dc51f7fc-da55-450b-b214-20d875e7687f.png)
    
    Note: By default username/password are set to "azure". This can be changed here "src/master/grafana/grafana.env"
 
5. Navigating Moneo Grafana Portal
    - The current view is labeled in the top left corner:
    
        ![image](https://user-images.githubusercontent.com/70273488/173687229-d1d64693-58d6-4874-a61c-c32af67e3fea.png)
    - VM instance and GPU can be selected from the drop down menus in the top left corner:

        ![image](https://user-images.githubusercontent.com/70273488/173687914-ee684e71-02a7-429e-abfa-046244e9eea0.png)
    - Various actions such as dashboard selection or data source configuration can be achieved using the left screen menu:

      ![image](https://user-images.githubusercontent.com/70273488/173689054-661bb442-4883-4f99-9147-b8307821a6b2.png)
    - Metric groups are collapsable:

      ![image](https://user-images.githubusercontent.com/70273488/173689514-e7532cfb-0b56-41ed-b9b9-1d71beaab123.png)

