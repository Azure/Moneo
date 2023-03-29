#!/bin/bash

WORK_DIR=$(dirname "${BASH_SOURCE[0]}")

PROF_METRICS=$1

START_PUBLISHER=$2

#shutdown previous instances
$WORK_DIR/shutdown.sh false

# start exporters
if [ -e "/dev/nvidiactl" ];
then
    nohup nv-hostengine </dev/null >/dev/null 2>&1 &
    if [ $PROF_METRICS = true ];
    then
        nohup python3 $WORK_DIR/exporters/nvidia_exporter.py -m </dev/null >/dev/null 2>&1 &
    else
        nohup python3 $WORK_DIR/exporters/nvidia_exporter.py  </dev/null >/dev/null 2>&1 &
    fi
elif [ -e '/dev/kfd' ];
then
    nohup /opt/rocm/rdc/bin/rdcd -u </dev/null >/dev/null 2>&1 &
    nohup python3 $WORK_DIR/exporters/amd_exporter.py </dev/null >/dev/null 2>&1 &
fi

nohup python3  $WORK_DIR/exporters/net_exporter.py </dev/null >/dev/null 2>&1 &
nohup python3  $WORK_DIR/exporters/node_exporter.py </dev/null >/dev/null 2>&1 &


if [ -n "$START_PUBLISHER" ]
then
    if [[ $START_PUBLISHER == "geneva" || $START_PUBLISHER == "azure_monitor" ]]
    then
        if [[ $START_PUBLISHER == "geneva" ]];
        then
            # check/start geneva docker
            $WORK_DIR/start_geneva.sh $WORK_DIR/publisher/config/geneva_config.json
        fi
        sleep 5
        nohup python3  $WORK_DIR/publisher/metrics_publisher.py $START_PUBLISHER </dev/null >/dev/null 2>&1 &
    else
        echo "Publisher not supported"
    fi
fi
