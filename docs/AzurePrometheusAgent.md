Azure Prometheus Agent User Guide (Preview)
=====
Description
-----
This guide will provide step-by-step instructions on how to use Azure Management to publish your exporter metrics in a second-level granularity interval.

Prequisites:
1. An Azure Monitor Workspace (AWM), a.k.a Azure Managed Prometheus resource.
2. Authentication
    User Managed Identity (umi)
    - Create an umi on azure portal, register umi object id on geneva portal with a metricsPublisher role, and add the Moneo service princple to the VM/VMSS
    - Navigate to your VM/VMSS resource on the portal.
    - From the left menu select "identity" ![image](https://user-images.githubusercontent.com/70273488/227347854-89a1fbaa-d9ca-4694-97fa-cac2fd59ea6f.png)
    - From the top tabs select "User assigned"
    - Then click on "Add" this will open a blade to search for the managed identities.
    - search and select "moneo-umi".
    - Click add at the bottom of the open blade.
2. PSSH installed on manager nodes.
3. Ensure passwordless ssh is installed in you environment.
4. Config sidecar config file in `Moneo/src/master/sidecar_config.json`.
    Note: You can obtain your IDENTITY_CLIENT_ID in your indentity resource page and your metrics ingestion endpoint from the AWM pages you created in the Azure portal.
    ```
        {
            "IDENTITY_CLIENT_ID": "<identity client id>",
            "INGESTION_ENDPOINT": "<metrics ingestion endpoint>"
        }
    ```
Steps
-----
1. Ensure that all prequisites are met.
2. deploy Moneo:
  - Full deployment 
  
    ```python3 moneo.py -d full --enable_prometheus -c ~/hostfile --manager_host localhost```
  - Master deployment
  
     ```python3 moneo.py -d master --enable_prometheus -c ~/hostfile```

    Note: if install step has already been performed you can use the -w flag to skip it.
3. Verify functionality of prometheus agent remote write :
    
    a. Check prometheus docker with `sudo docker logs prometheus | grep 8081`
    It will have the result like this:
    ```
        ts=2023-04-26T10:20:21.722Z caller=dedupe.go:112 component=remote level=info remote_name=c35834 url=http://localhost:8081/api/v1/write msg="Starting WAL watcher" queue=c35834

        ts=2023-04-26T10:20:21.722Z caller=dedupe.go:112 component=remote level=info remote_name=c35834 url=http://localhost:8081/api/v1/write msg="Starting scraped metadata watcher"

        ts=2023-04-26T10:20:21.722Z caller=dedupe.go:112 component=remote level=info remote_name=c35834 url=http://localhost:8081/api/v1/write msg="Replaying WAL" queue=c35834

        ts=2023-04-26T10:20:27.156Z caller=dedupe.go:112 component=remote level=info remote_name=c35834 url=http://localhost:8081/api/v1/write msg="Done replaying WAL" duration=5.434237136s   
    ```
    Which means, prometheus agent 's remote write function is enabled to port 8081.
    
    b. Check the sidecar docker's status with `netstat -tupln | grep 8081`

    It will have the result like this:
    ```
        tcp6       0      0 :::8081                 :::*                    LISTEN      -    
    ```
    Which means, port 8081 is under listening by prometheus sidecar docker.
4. At this point the remote write functionality shoud be working.
5. Check with Azure grafana (linked with AMW )dashboards to verify that the metrics are being ingested.
