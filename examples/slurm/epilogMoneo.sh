#!/bin/bash

echo $SLURM_JOB_ID > /tmp/testfile.txt

# The command below pipes stdout/stderr to files, This is necessary for ansible to behave correctly.
sudo -u <Your user> -H sh -c "cd  <Moneo DIR> &&  python3 moneo.py -j None -c /tmp/jobid_$SLURM_JOB_ID.txt >> /tmp/$SLURM_JOB_NAME.$SLURM_JOB_ID.Moneo.log 2>&1"

rm /tmp/jobid_$SLURM_JOB_ID.txt

exit 0


