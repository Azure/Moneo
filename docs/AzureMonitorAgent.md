Azure Monitor Metrics User Guide
=====
Description
-----
This guide will provide step-by-step instructions on how to share your exporter metrics with Azure by utilizing Azure Monitor Metrics.

Prequisites:
1. An Azure Monitor Metrics (Application Insights) resource, please enable alerting on custom metric dimensions by refering this [document](https://learn.microsoft.com/en-us/azure/azure-monitor/app/pre-aggregated-metrics-log-metrics#custom-metrics-dimensions-and-pre-aggregation) to restore the metrics dimentions.(Lead to a extra cost)
2. PSSH installed on manager nodes.
3. Ensure passwordless ssh is installed in you environment.
4. Config publisher config file in `Moneo/src/worker/publisher/config/publisher_config.json`.
    Note: You can obtain your connection string from the Application Insights pages you created in the Azure portal.
    ```
    {
        "common_config": {
            "metrics_ports": "8000,8001,8002",
            "metrics_namespace": "<your_metrics_namespace>",
            "interval": "20"
        },
        "geneva_agent_config": {
            "metrics_account": "<metrics_account>"
        },
        "azure_monitor_agent_config": {
            "connection_string": "<your_connectionString>"
        }
    }
    ```
Steps
-----
1. Ensure that all prequisites are met.
2. deploy Moneo:
  - Full deployment 
  
    ```python3 moneo.py -d full -g azure_monitor -c ~/hostfile --manager_host localhost```
  - Worker deployment
  
     ```python3 moneo.py -d workers -g azure_monitor -c ~/hostfile```

    Note: if install step has already been performed you can use the -w flag to skip it.
3. Verify that the exporters and publisher are running with `ps -aux | grep python3`

    It will have the result like this:
    ```
    root      811921  6.0  0.0 344292 41536 ?        Rl   09:32   0:00 python3 /tmp/moneo-worker/exporters/nvidia_exporter.py
    root      811922  3.1  0.0 175820 21196 ?        Sl   09:32   0:00 python3 /tmp/moneo-worker/exporters/net_exporter.py
    root      811923  2.0  0.0 102620 21520 ?        Sl   09:32   0:00 python3 /tmp/moneo-worker/exporters/node_exporter.py
    root      811992 38.0  0.0 644868 46536 ?        Sl   09:32   0:00 python3 /tmp/moneo-worker/publisher/metrics_publisher.py azure_monitor
    ```
4. At this point the exporters and publisher shoud be working.
5. Check with Azure Monitor Metrics (Application Insights) dashboards to verify that the metrics are being ingested.
