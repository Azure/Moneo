#!/bin/bash


# Usage:
# Managed Prometheus deployment: ./start_moneo_services.sh 
# Azure Monitor: ./start_moneo_services.sh azure_monitor
# Geneva (internal msft): ./start_moneo_services.sh geneva
# Only start workers: ./start_moneo_services.sh workers
PublisherMethod=$1 

# Modify as necessary
MONEO_PATH=/opt/azurehpc/tools/Moneo
PUBLISHER_AUTH=umi # other choice is cert

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path does not exist. Please install Moneo and/or provide the full path to this script. Exiting start script"
    exit 1
fi


procs=("net_exporter" "node_exporter")

if lspci | grep -iq NVIDIA ; then
    procs+=("nvidia_exporter")
fi

if [[ -n $PublisherMethod ]] ; then
    if [ "$PublisherMethod" == "geneva" ] || [ "$PublisherMethod" == "azure_monitor" ]; then
        echo "PublisherMethod is valid: $PublisherMethod"
        procs+=("metrics_publisher")
    elif [ "$PublisherMethod" == "workers" ]; then
        echo "Only starting workers"
    else
        echo "PublisherMethod is not one of the valid choices."
        exit 1
    fi
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
        if [[ $(sudo docker ps -a | grep prometheus) ]] ; then
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

sudo systemctl enable moneo@node_exporter.service
sudo systemctl enable moneo@net_exporter.service
sudo systemctl enable moneo@nvidia_exporter.service

sudo systemctl start moneo@node_exporter.service
sudo systemctl start moneo@net_exporter.service
sudo systemctl start moneo@nvidia_exporter.service

if [ "$PublisherMethod" == "workers" ]; then
    proc_check false
fi

if [[ -n $PublisherMethod ]]; then
    if [ "$PublisherMethod" == "geneva" ]; then
        sudo $MONEO_PATH/src/worker/start_geneva.sh $PUBLISHER_AUTH /tmp/moneo-worker/publisher/config
    fi
    sleep 10 # wait a bit for the exporters to start
    sudo systemctl enable moneo_publisher.service
    sudo systemctl start moneo_publisher.service 
    proc_check false
else
    sudo $MONEO_PATH/src/worker/start_managed_prometheus.sh 2> /dev/null
    sleep 10 # wait a bit for the exporters to start
    proc_check true
fi
