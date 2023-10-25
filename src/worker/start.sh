#!/bin/bash

WORK_DIR=$(dirname "${BASH_SOURCE[0]}")

PROF_METRICS=$1

START_PUBLISHER=$2

PUBLISHER_AUTH=${3:-""}

CUTSOM_METRICS_PATH=${4:-""}
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
if [[ -n "$CUTSOM_METRICS_PATH" ]]
then
    nohup python3  $WORK_DIR/exporters/custom_exporter.py --custom_metrics_file_path $CUTSOM_METRICS_PATH </dev/null >/dev/null 2>&1 &
fi

if [ -n "$START_PUBLISHER" ]
then
    if [[ $START_PUBLISHER == "geneva" || $START_PUBLISHER == "azure_monitor" || $START_PUBLISHER == "managed_prometheus" ]]
    then
        if [[ $START_PUBLISHER == "geneva" ]];
        then
            if [ -n "$PUBLISHER_AUTH" ]
            then
                if [[ $PUBLISHER_AUTH == "umi" || $PUBLISHER_AUTH == "cert" ]];
                then
                    # Start Geneva Metrics Extension(MA) docker container with UMI
                    echo "Starting Geneva Metrics Extension(MA) docker container with $PUBLISHER_AUTH"
                    $WORK_DIR/start_geneva.sh $PUBLISHER_AUTH $WORK_DIR/publisher/config
                else
                    # Unsupported auth type
                    echo "Publisher auth not supported"
                fi
            fi
        elif [[ $START_PUBLISHER == 'managed_prometheus' ]];
        then
            echo "Starting Managed Prometheus"
            $WORK_DIR/start_managed_prometheus.sh
        fi
        sleep 5
        nohup python3  $WORK_DIR/publisher/metrics_publisher.py $START_PUBLISHER >> /tmp/metrics_publisher.log 2>&1 &
    else
        echo "Publisher not supported"
    fi
fi
