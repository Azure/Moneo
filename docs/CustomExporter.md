Custom Exporter User Guide
============================

Description
-----------
In addition to the existing exporters like the NVIDIA exporter (GPU level), IB exporter (Infiniband level), and node exporter (Node level), Moneo also provides support for a custom exporter, allowing users to expose their own metrics. These custom metrics can include training loss, training accuracy, and more.

Steps
-----
1. Create a JSON file to define your custom metrics following a format similar to the examples below:

   - If you want to expose GPU-related metrics for a specific GPU device, use the format `gpu_<gpu_id>_<metric_name>: <metric_value>`. The resulting metric will be named `gpu_<metric_name>` with a label `gpu_id` corresponding to the specified GPU ID.

   - If you want to expose Infiniband (IB) related metrics, use the format `ib_<ib_port>_<metric_name>: <metric_value>`. The resulting metric will be named `ib_<metric_name>` with a label `ib_port` corresponding to the specified IB port.

   - If you simply want to define a metric without any specific label, use the format `<metric_name>: <metric_value>`. This metric will not have any associated labels.

   Here is a template for a custom_metrics_file in JSON format:

   ```json
   {
       "gpu_0_metric1": 1.0,
       "gpu_1_metric1": 1.0,
       "gpu_2_metric1": 1.0,
       "gpu_3_metric1": 1.0,
       "ib_0_metric2": 1.0,
       "ib_1_metric2": 1.0,
       "ib_2_metric2": 1.0,
       "ib_3_metric2": 1.0,
       "metric3": 1.0,
       "metric4": 1.0
   }
   ```

2. Start Moneo with the following command, specifying the path to your custom metrics file and enabling the custom_exporter on port `8003`:

   ```bash
   python3 moneo.py -d -c <host_file> --custom_metrics_file_path <custom_metrics_file_path>
   ```

3. Verify that the custom-exporter is functioning correctly by accessing the Prometheus metrics using the following command:

   ```bash
   curl localhost:8003
   ```

   You should see metrics similar to the following, indicating that the custom-exporter is working as expected:

   ```plaintext
   ...
   # HELP custom_gpu_metric1 custom_gpu_metric1
   # TYPE custom_gpu_metric1 gauge
   custom_gpu_metric1{gpu_id="0",job_id="None"} 1.0
   custom_gpu_metric1{gpu_id="1",job_id="None"} 1.0
   custom_gpu_metric1{gpu_id="2",job_id="None"} 1.0
   custom_gpu_metric1{gpu_id="3",job_id="None"} 1.0
   # HELP custom_ib_metric2 custom_ib_metric2
   # TYPE custom_ib_metric2 gauge
   custom_ib_metric2{ib_port="mlx5_ib0:1",job_id="None"} 1.0
   custom_ib_metric2{ib_port="mlx5_ib1:1",job_id="None"} 1.0
   custom_ib_metric2{ib_port="mlx5_ib2:1",job_id="None"} 1.0
   custom_ib_metric2{ib_port="mlx5_ib3:1",job_id="None"} 1.0
   # HELP custom_metric3 custom_metric3
   # TYPE custom_metric3 gauge
   custom_metric3{job_id="None"} 1.0
   # HELP custom_metric4 custom_metric4
   # TYPE custom_metric4 gauge
   custom_metric4{job_id="None"} 1.0
   ...
   ```

Please note that this guide assumes that you have already set up the necessary environment and dependencies for running Moneo.