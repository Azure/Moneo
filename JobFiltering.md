Moneo Job Level Filtering
=====
Description
-----
Moneo provides a way to designate a job name/Id for nodes participating in a job. The Job Id can be used to filter on nodes that belong to a specific job. 

Steps
-----
Moneo must be already deployed and running on the cluster where job grouping will be designated.
1. To set a job Id to a subset of nodes a config.ini file with the desired hosts must be passed in:
*  ```python3 moneo.py -j 4 -c host.ini```
* The 'host.ini' file will be the same format as the config file used to deploy Moneo for the exception that the worker list will only include the hosts for the job group.
* i.e. 
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
 * The hosts listed under the worker label will be part of the specified job group.
2. The ```python3 moneo.py -j 4 -c host.ini``` command can be used in a job scheduling script such as a PBS scipt, Sbatch script or called manually from command line.
3. At the completion of the of the job ```python3 moneo.py -j None -c host.ini``` command can be called again with either "None" or some default Job ID. AGain this can be put at the end of a job scheduling script.

Portal View
-----
1. Once the Job Id has been specified using the moneo CLI command the Job Ids should populate the Grafana portal:
![image](https://user-images.githubusercontent.com/70273488/184166034-7ddddb6f-c2d5-4b30-9ebd-8b66087239a6.png)
Note: This might require a browser refresh for recent Job ID updates.
 
