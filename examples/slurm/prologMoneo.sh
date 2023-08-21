#!/bin/bash

job_id="$SLURM_JOB_ID"
job_name="$SLURM_JOB_NAME"

if [ -z "$job_name" ]; then
    job_name='slurm_job'
fi

log_file=/tmp/moneo-worker/id_change.log

sudo /tmp/moneo-worker/jobIdUpdate.sh  "${job_name}_${job_id}" > "$log_file" 2>&1

exit 0
