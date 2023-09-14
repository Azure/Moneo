# Managed Grafana Deployment #

- The following steps assume the Moneo directory is located here: /opt/azurehpc/tools/Moneo
- The following steps deploy Moneo workers using Moneo linux services, however Az CLI can also be used to deploy the Moneo workers. See [managed prometheus guide](./ManagedPrometheusAgent.md) for details on how.
- Moneo CLI can be used in place of Moneo linux services to deploy Moneo workers

## Deploy Infrastructure ##

To use this method you will need to deploy the managed infrastructure and managed user identity.

Follow steps outlined in [Infrastructure deployment](../deploy_managed_infra/README.md) to setup Azure Managed Grafana and Prometheus resources.

  Note: this only needs to be done once.

## Deploy Moneo ##

1. Modify the managed prometheus config file in `Moneo/src/worker/publisher/config/managed_prom_config.json`.
    - Reference the user managed identity created during infrastructure deployment to get the "identity client id"
    - Reference the Managed Prometheus resource created during infrastructure deployment to get the "metrics ingestion endpoint"
    - The config file modifcations must be distributed to the Moneo directories on all workers.
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

5. Check with Azure Grafana Dashboards to verify that the metrics are being ingested.

    ![image](assets/azuregrafana-managed_prometheus.png)
