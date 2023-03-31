#!/bin/bash

echo $SLURM_JOB_NODELIST > /tmp/jobid_$SLURM_JOB_ID.txt

# The command below pipes stdout/stderr to files, Moneo will still update the respective moneo logs 
sudo -u <Your user> -H sh -c "cd  <Moneo Dir> &&  python3 moneo.py -j $SLURM_JOB_NAME.$SLURM_JOB_ID -c /tmp/jobid_$SLURM_JOB_ID.txt > /tmp/$SLURM_JOB_NAME.$SLURM_JOB_ID.Moneo.log 2>&1"

exit 0

