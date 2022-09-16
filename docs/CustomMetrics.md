How to export my own custom metrics
=====
Description
-----
Moneo provides a way for you to export your own custom node metrics. This will require you to modify/create your own custom exporter script. The [BaseExporter](./src/worker/exporters/base_exporter.py) parent class is provided for so that a child class can be created to export your custom metrics.

Additionally a [NodeExporter](./src/worker/exporters/node_exporter.py) class is provided as an example of how to create a custom exporter. You may choose to modify this as it is already integrated to the rest of the Moneo deployment process. If you choose to to create a new exporter you will have some additional modifications you will need to make (explained the Steps section). 

The Node Exporter Overview
-----
The node exporter is a child class of the base exporter class. The base exporter defines the functions needed to collect and send telemetry to the Prometheus database. 
### Init and Required Arguments
The init function is pretty straight forward and requires 2 arguments. 
- A list of the metrics to be collected:
```FIELD_LIST = ['net_rx', 'net_tx']```
- A config dictionary:
```
    config = {
        'exit': False, # default
        'update_freq': 1, # update frequency in seconds
        'listen_port': port, # port number
        'publish_interval': 1, # publish frequency in seconds
        'job_id': job_id, # the default job id should be None.
        'fieldFiles': {}, # Location of files needed for retrieving telemetry
        'counter': {} # Intermediate storage of metric values. COuld be used to store old values to calculate bandwidth
    }
```
### Necessary Modifications
The node exporter defines 2 functions that the parent class leaves unimplemented. The collect and cleanup functions:
- The collect function in this example is used to gather network tx/rx data from the /proc/net/dev file. It issues an OS command to grab the relevant data and parse the correct value. 
- The cleanup function is called right before the exporter exits. It is most useful if you need to close any open files.

Note: Other utiliy functions are described in the Steps section.

### Integration
The following files have been modified to integrate the node exporter to the rest of the Moneo workflow:
-    src/ansible/deploy.yaml
-    src/ansible/prometheus.config.j2
-    src/ansible/updateJobID.yaml
-    src/master/prometheus.yml
-    src/worker/shutdown.sh


Steps
-----
1. If you choose to use/modify the node exporter example provided skip to step 6, otherwise continue to step 2.
2. Create a child class for your custom metrics. Ensure to include the BaseExporter as you parent class.
3. You will need to create 3 functions within the class. Class functions needed:
   -  \_\_init\_\_(self, node_fields, exp_config)
       - This function will initialize the class and the parent class. You must pass in a list of your metrics and a config dictionary (see NodeExporter for example).
   -   collect(self, field_name)
       - This function will be what is actually collecting your metrics. For example it may open a file and parse it for a give metric. 
   -   cleanup(self)
       - This function will be called right before exit. SO it could be used to close any open files or print a message.
4. In addition to the class you will need to have the following supporting functions:
   - A function that initializes a config dictionary to pass to the exporter.
      - See init_config function in the NodeExporter example.
      - This function may require you to modify things like update interval, communication port, and/or initial counter value
   - init_signal_handler and  get_log_level can be copied directly from the NodeExporter example
   - The main function can be copied directly from NodeExporter. You may choose to add more arguments for the arg parser
5. Integration (If you are modifying the NodeExporter DO NOT perform these steps):
   - [deploy.yaml](./src/ansible/deploy.yaml): in the deploy work section add a block to deploy the exporter via shell. (Reference the other blocks that launch exporters).
   - prometheus config files [manager config](./src/master/prometheus.yml) [ansible config](./src/ansible/prometheus.config.j2) : Reference the other exporters' configurations.
   - [job update config](./src/ansible/updateJobID.yaml): reference other exporter ansible blocks.
   - [shutdownscripts](./src/worker/shutdown.sh): perform the same command as used on other exporters
 6. At this point if the above steps are completed properly you should be able to view/query the metric using Prometheus UI. 
    - On your browser go to \<IP-manager-node\>:9090
    - Query for your metric i.e. ![image](https://user-images.githubusercontent.com/70273488/189758490-9949e332-b025-4afd-a6d3-8b402950ca46.png)
 7. Once the above steps are complete you can start creating custom graphs/dashboards on Grafana. Make sure to export and save the modified/new dashboards to this directory:
  /src/master/grafana/dashboards/ 
  


