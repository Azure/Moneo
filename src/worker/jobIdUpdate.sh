#!/bin/bash
# this script could be run from a prolog and epilog script
JOB_ID=$1

#create file w/ job id so the exporters can read.
echo $JOB_ID > /tmp/moneo-worker/curr_jobID

#update jobid for nv exporter
if [ -e "/dev/nvidiactl" ];
then
    nv_pid=`pgrep -fx  ".*python3 .*nvidia_exporter.py.*"`
    if [ "$nv_pid"!="" ];
    then
        kill -USR1 $nv_pid
    fi
fi
#update jobid for IB exporter
if [ -d "/sys/class/infiniband" ];
then
    ib_pid=`pgrep -fx ".*python3 .*net_exporter.py.*"`
    if [ "$ib_pid"!="" ];
    then
        kill -USR1 $ib_pid
    fi
fi
#update jobid for node exporter
node_pid=`pgrep -fx ".*python3 .*node_exporter.py.*"`
if [ "$node_pid"!="" ];
then
    kill -USR1 $node_pid
fi
#update jobid for custom exporter
custom_pid=`pgrep -fx ".*python3 .*custom_exporter.py.*"`
if [ "$custom_pid"!="" ];
then
    kill -USR1 $custom_pid
fi
