#!/bin/bash

echo $SLURM_JOB_ID > /tmp/testfile.txt

# The command below pipes stdout/stderr to files, This is necessary for ansible to behave correctly.
sudo -u <Your user> -H sh -c "cd  <Moneo DIR> &&  python3 moneo.py -j None -c /tmp/jobid_$SLURM_JOB_ID.txt  >> /tmp/moneolog.out  2>> /tmp/moneolog.err "

exit 0


