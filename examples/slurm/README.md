# Moneo Job Id Update Integration w/ Slurm #

## Description ##

-----
Moneo allows for the assignment of job IDs to a subset of nodes. The running command ```/tmp/moneo-worker/jobIdUpdate.sh <jobid>``` on each compute node accomplishes this.

Doing this manually may be tedious if the frequency of job deployment is high. Integrating job updates into Slurm's Prolog/Epilog scripts will offload the effort from the individual user launching a job on Slurm.

## Requirements ##

-----

- Moneo must be deployed to the compute nodes prior to job creation.

## Preffered Moneo configuration: Moneo Linux services ##

-----
Configure Moneo Linux service: [Moneo services](../../linux_service/README.md)

This makes managing Moneo easier.

## Steps ##

-----

1. Place the [prolog](./prologMoneo.sh) and [epilog](./epilogMoneo.sh) scripts in a directory which will be pointed to by the Slurm configuration.

2. Next modify the /etc/slurm.conf file by adding the following variables:

    ``` Bash
        Prolog=/mnt/sched/slurm/etc/prologMoneo.sh
        PrologFlags=Alloc
        Epilog=/mnt/sched/slurm/etc/epilogMoneo.sh
    ```

    Note:  This will allow the scripts to be run on each compute node

3. Restart slurmctld and slurmd:

    ``` Bash
        sudo systemctl restart slurmctl
    ```

    ``` Bash
        parallel-ssh -h hostfile -i -t 0 "sudo systemctl restart slurmd"
    ```

    Note: This will allow for the new config to be loaded

4. At this point Moneo will now update job Ids when slurm jobs start.

    - If there are issues please check that Moneo is running on all nodes.
    - Check the "log_file" to check output from the job id update command.
