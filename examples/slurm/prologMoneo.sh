#!/bin/bash

echo "[worker]" > /tmp/jobid_$SLURM_JOB_ID.txt
echo $SLURM_JOB_NODELIST >> /tmp/jobid_$SLURM_JOB_ID.txt

# The command below pipes stdout/stderr to files, This is necessary for ansible to behave correctly. 
sudo -u <Your user> -H sh -c "cd  <Moneo Dir> &&  python3 moneo.py -j $SLURM_JOB_NAME.$SLURM_JOB_ID -c /tmp/jobid_$SLURM_JOB_ID.txt  > /tmp/moneolog.out 2>&1"

exit 0

