#!/bin/bash

MONEO_PATH=$1
PUBLISHER=$2

if [[ -z "$MONEO_PATH" ]];
then
    MONEO_PATH=/opt/azurehpc/tools/Moneo
    echo 'default Moneo path used'
fi

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path $MONEO_PATH does not exist. Ensure you are using the correct arguments  
    (i.e. ./configure_service.sh <Moneo_path>, or ./configure_service.sh <Moneo_path> <publisher-type>). Exiting." 
    exit 1
fi

if [[ -n $PUBLISHER  ]];
then
    if [ "$PUBLISHER" != "geneva" ] && [ "$PUBLISHER" != "azure_monitor" ];
    then
        echo "Error: $PUBLISHER is not an acceptable value for publisher type. Options are 'geneva' or 'azure_monitor'. Exiting."
        exit 1
        
    fi
fi

# replace the moneo path place holder with actaul moneo path and Move service file to systemd directory
sed  "s#<Moneo_Path>#$MONEO_PATH#g" $MONEO_PATH/linux_service/moneo@.service > /etc/systemd/system/moneo@.service

if [[ -n $PUBLISHER  ]];
then
    sed  "s#<Moneo_Path>#$MONEO_PATH#g; s#<pub-type>#$PUBLISHER#g;" $MONEO_PATH/linux_service/moneo_publisher.service > /etc/systemd/system/moneo_publisher.service
fi

systemctl daemon-reload

# enable exporter services
systemctl enable moneo@node_exporter.service
systemctl enable moneo@net_exporter.service
systemctl enable moneo@nvidia_exporter.service
if [[ -n $PUBLISHER  ]];
then
    systemctl enable moneo_publisher.service
fi
