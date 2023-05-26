#!/bin/bash
WITH_PUBLISHER=$3
WITH_MANAGED_PROM=$2
MONEO_PATH=$1

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path does not exist. Please install Moneo and/or provide the full path to this script. Exiting start script"
    exit 1
fi

procs=("net_exporter" "node_exporter")

if lspci | grep -iq NVIDIA ; then
    procs+=("nvidia_exporter")
fi

if [[ -n $WITH_PUBLISHER && $WITH_PUBLISHER = true ]]; then
    procs+=("metrics_publisher")
fi

function proc_check(){
    CHECK=`ps -eaf | grep /tmp/moneo-worker/`
    for substring in "${procs[@]}"; do
        if [[ $CHECK == *"$substring"* ]]; then
            echo "$substring service started as expected."
        else
            echo "Some services failed to start"
            exit 1
        fi
    done
    if [[ -n $WITH_MANAGED_PROM && $WITH_MANAGED_PROM = true ]];
    then
        if [[ $(docker ps -a | grep prometheus_sidecar) &&  $(docker ps -a | grep prometheus) ]] ; then
            echo "Prometheus and Prometheus_side_car docker containers running."
        else
            echo "Prometheus and/or Prometheus_side_car failed to start. Please ensure you have the proper user managed identity assigned to your VMSS/VM. (moneo-umi)"
            exit 1
        fi
    fi
    echo "All Services Running"
    exit 0
}


systemctl enable moneo@node_exporter.service
systemctl enable moneo@net_exporter.service
systemctl enable moneo@nvidia_exporter.service

systemctl start moneo@node_exporter.service
systemctl start moneo@net_exporter.service
systemctl start moneo@nvidia_exporter.service

if [[ -n $WITH_MANAGED_PROM && $WITH_MANAGED_PROM = true ]]; then
    $MONEO_PATH/src/worker/start_managed_prometheus.sh
fi

if [[ -n $WITH_PUBLISHER && $WITH_PUBLISHER = true ]]; then
    sleep 5 # wait a bit for the exporters to start
    systemctl enable moneo_publisher.service
    systemctl start moneo_publisher.service 
fi

proc_check
