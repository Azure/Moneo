#!/bin/bash

# Managed Prometheus deployment: ./configure_service.sh 
# Azure Monitor: ./configure_service.sh  azure_monitor
# Geneva (internal msft): ./configure_service.sh geneva

PublisherMethod=$1 

if [[ -n $PublisherMethod ]]; then
    if [ "$PublisherMethod" == "geneva" ] || [ "$PublisherMethod" == "azure_monitor" ]; then
        echo "PublisherMethod is valid: $PublisherMethod"
    else
        echo "PublisherMethod $PublisherMethod is not one of the valid choices {azure_monitor, geneva}."
        exit 1
    fi
fi

MONEO_PATH=/home/rafsalas/Moneo

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path $MONEO_PATH does not exist. Ensure you have Moneo directory in this path $MONEO_PATH"
    exit 1
fi

# replace the moneo path place holder with actaul moneo path and Move service file to systemd directory
cp $MONEO_PATH/linux_service/moneo@.service  /etc/systemd/system/moneo@.service

echo "configuring publisher service" 
if [[ "$PublisherMethod" == "geneva" ]]; then
    # writes to the same file location as Azure monitor
    cp $MONEO_PATH/linux_service/geneva_publisher.service /etc/systemd/system/moneo_publisher.service
    $MONEO_PATH/src/worker/install/install.sh geneva 
else
    cp $MONEO_PATH/linux_service/moneo_publisher.service /etc/systemd/system/moneo_publisher.service
    $MONEO_PATH/src/worker/install/install.sh azure_monitor
fi

systemctl daemon-reload
