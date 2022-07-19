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
    python3 -m pip install ansible
    ```
    Note: If you are using an [Azure Ubuntu HPC-AI](https://github.com/Azure/azhpc-images) VM image you can find the Moneo in this path: /opt/azurehpc/tools/Moneo

2. Next create a host.ini config file.  
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
    Note: The master node can also be work node as well. The master node will have the Grafana and Prometheus docker containers deployed to it.
    
    Note: If you have configured passwordless SSH already, `[all:vars]` section can be skipped.
    
    Note: The master node must be able to ssh into itself
    
3. Now deploy Moneo
    * using Moneo cli:
    ```sh 
    python3 moneo.py --deploy full -c host.ini -j 0
    ```
    note: see usage section of the README doc for more details on Moneo CLI 
    * manual deployment
    ```sh
    ansible-playbook -i host.ini src/ansible/deploy.yaml
    ```    
4. Log into the portal by navigating to `http://master-ip-or-domain:3000` and inputting your credentials
    ![image](https://user-images.githubusercontent.com/70273488/173685955-dc51f7fc-da55-450b-b214-20d875e7687f.png)
    
    Note: By default username/password are set to "azure". This can be changed here "src/master/grafana/grafana.env"
 
5. Navigating Moneo Grafana Portal
    - The current view is labeled in the top left corner:
    
        ![image](https://user-images.githubusercontent.com/70273488/179831203-b9381265-1213-4a86-92c2-c820658afb0e.png)
    - Job, VM instance, and GPU level filtering can be controlled from the drop down menus in the top left corner:

        ![image](https://user-images.githubusercontent.com/70273488/179831061-48576722-9e00-4e2e-bdf1-28a8d9c99998.png)
    - Various actions such as dashboard selection or data source configuration can be achieved using the left screen menu:

      ![image](https://user-images.githubusercontent.com/70273488/173689054-661bb442-4883-4f99-9147-b8307821a6b2.png)
    - Metric groups are collapsable:

      ![image](https://user-images.githubusercontent.com/70273488/173689514-e7532cfb-0b56-41ed-b9b9-1d71beaab123.png)

