# Moneo Quick Start Guide #

## Preffered Moneo Deployment ##

-----

The preffered method to deploy Moneo is by using Azure Managed Grafana and Prometheus resources.

- This method does not require a head node as Grafana and Prometheus are managed by Azure.
- If using Azure AI/HPC market place image dependencies and requirements will be met.
- The following steps assume the Moneo directory is located here: /opt/azurehpc/tools/Moneo
- The following steps deploy Moneo workers using Moneo linux services, however Az CLI can also be used to deploy the Moneo workers. See [managed prometheus guide](./ManagedPrometheusAgent.md) for details on how.

### Deploy Managed Infrastructure ####

1. Follow steps outlined in [Infrastructure deployment](../deploy_managed_infra/README.md) to setup Azure Managed Grafana and Prometheus resources.

    Note: this step only needs to be done once.

### Deploy Moneo ###

1. Modify the managed prometheus config file in `Moneo/src/worker/publisher/config/managed_prom_config.json`.
    - Reference the user managed identity created during infrastructure deployment to get the "identity client id"
    - Reference the Managed Prometheus resource created during infrastructure deployment to get the "metrics ingestion endpoint"

    ```json
    {
        "IDENTITY_CLIENT_ID": "<identity client id>",
        "INGESTION_ENDPOINT": "<metrics ingestion endpoint>"
    } 
    ```

2. Assign the identity to your VMSS resource:
    - This can either be done via the portal or AZ CLI (below)
    - During VMSS creation:

        ```sh
        az vmss create --resource-group <RESOURCE GROUP> --name <VMSS NAME> --image <SKU Linux Image> --admin-username <USER NAME> --admin-password <PASSWORD> --assign-identity <USER ASSIGNED IDENTITY> --role <ROLE> --scope <SUBSCRIPTION>
        ```

    - Already existing VMSS:

        ```sh
            az vmss identity assign -g <RESOURCE GROUP> -n <VIRTUAL MACHINE SCALE SET NAME> --identities <USER ASSIGNED IDENTITY>
        ```

3. Start Services (Assumes Azure marketplace AI/HPC Image): ``` parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/start_moneo_services.sh true" ```
    - To stop services: ```parallel-ssh -i -t 0 -h hostfile "sudo /opt/azurehpc/tools/Moneo/linux_service/stop_moneo_services.sh"```

    Note: If not using Azure AI/HPC market place image reference the ["Deploying Linux services guide"](../linux_service/README.md) for full instructions.

4. At this point data collection should be on going and metrics streaming to the Azure managed Grafana setup during infrastructure.

    Note: In the infrastructure deployment step you have the option to use provided template dashboards or create your own.

## Alternative deployment using Az CLI and head node ##

-----

This method requires a deployment of a head node to host the local Prometheus Database and Grafana server.

- The headnode must have enough storage available to facilitate data collection
- Grafana and Prometheus is accessed by a web browser. So the corresponding browser must have access to the head nodes IP.

1. Clone Moneo from Github.

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
    - using Moneo cli:

    ```sh
        python3 moneo.py --deploy -c hostfile full
    ```

    - If using the Azure HPC/AI marketplace image or if installation has been performed on all worker nodes by a previous deployment we can skip the install step:

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
