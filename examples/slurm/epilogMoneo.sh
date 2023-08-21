#!/bin/bash
log_file=/tmp/moneo-worker/id_change.log

sudo /tmp/moneo-worker/jobIdUpdate.sh  "None" > "$log_file" 2>&1

exit 0
