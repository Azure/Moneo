Moneo Job Id Update Integration w/ Slurm
=====
Description
-----
Moneo allows for the assignment of job IDs to a subset of nodes. The command ```python3 moneo.py -j <jobid> -c <job host.ini file>``` accomplishes this. The command requires a host.ini file which has a specific format. It also requires a job Id.

The host.ini has the following format:
```
host-1
host-2
host-3
```
Doing this manually may be tedious if the frequency of job deployment is high. Integrating job updates into Slurm's Prolog/Epilog scripts will offload the effort from the individual user launching a job on Slurm.

Requirements
-----
- Moneo must be deployed prior to job creation.
- The subset of nodes in a job must be within the nodes being monitored already by Moneo.

Steps
-----
1. Place the [prolog](./prologMoneo.sh) and [epilog](./epilogMoneo.sh) scripts in a directory which will be pointed to by the Slurm configuration.

    Note: The prolog script creates a host.ini file and gathers the Slurm job name and ID. It then will update the job Id (job Id $SLURM_JOB_NAME.$SLURM_JOB_ID). 

    Note: The epilog script will update the job Id to "None" then delete the host.ini file.

2. Next modify the /etc/slurm.conf file by adding the following variables:
    ```
    PrologSlurmctld=<prolog dir path>/prologMoneo.sh
    EpilogSlurmctld=<epilog dir path>/epilogMoneo.sh
    ```

    Note:  PrologSlurmctld and EpilogSlurmctld variables will enable the Slurm daemon to run the scripts on the head/scheduler node. The prolog will be run at the commencment of the job and the epilog script will run when it has ended. 

3. Restart slurmctld:
    ```
    sudo slurmctld restart
    ```

    Note: This will allow for the new config to be loaded

4. At this point Moneo will now update job Ids based off when a Slurm job is start and completed.




