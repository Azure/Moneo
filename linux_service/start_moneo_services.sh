#!/bin/bash
WITH_AZ_MON=$1

# Two modes of operation managed prometheus (default) and  az monitor (WITH_AZ_MON) enabled w/ WITH_AZ_MON=true

# User can modify this if they need to change
MONEO_PATH=/opt/azurehpc/tools/Moneo


if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path does not exist. Please install Moneo and/or provide the full path to this script. Exiting start script"
    exit 1
fi


procs=("net_exporter" "node_exporter")

if lspci | grep -iq NVIDIA ; then
    procs+=("nvidia_exporter")
fi

if [[ -n $WITH_AZ_MON && $WITH_AZ_MON = true ]]; then
    procs+=("metrics_publisher")
fi

function proc_check(){
    CHECK=`ps -eaf | grep /tmp/moneo-worker/`
    WITH_MANAGED_PROM=$1
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
        if [[ $(docker ps -a | grep prometheus) ]] ; then
            echo "Prometheus docker containers running."
        else
            echo "Prometheus failed to start. Please ensure you have the proper user managed identity assigned to your VMSS/VM."
            exit 1
        fi
    fi
    echo "All Services Running"
    exit 0
}

$MONEO_PATH/linux_service/moneo_prestart.sh $MONEO_PATH 2> /dev/null

systemctl enable moneo@node_exporter.service
systemctl enable moneo@net_exporter.service
systemctl enable moneo@nvidia_exporter.service

systemctl start moneo@node_exporter.service
systemctl start moneo@net_exporter.service
systemctl start moneo@nvidia_exporter.service

if [[ -n $WITH_AZ_MON && $WITH_AZ_MON = true ]]; then
    sleep 5 # wait a bit for the exporters to start
    systemctl enable moneo_publisher.service
    systemctl start moneo_publisher.service 
    proc_check false
else
    $MONEO_PATH/src/worker/start_managed_prometheus.sh 2> /dev/null
    sleep 5
    proc_check true
fi
