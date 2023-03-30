#!/bin/bash
PUBLISHER=$1
MONEO_PATH=$2

systemctl start moneo@node_exporter.service
systemctl start moneo@net_exporter.service
systemctl start moneo@nvidia_exporter.service

if [[ ! -z "$PUBLISHER" ]];
then
    if [ "$PUBLISHER" = "geneva" ] && [ -d $MONEO_PATH ];
    then
        #starts Geneva agent
        $MONEO_PATH/src/worker/start_geneva.sh  $MONEO_PATH/src/worker/publisher/config/geneva_config.json
        sleep 5 # wait a bit for the exporters to start
        systemctl start moneo_publisher.service 
    elif [ "$PUBLISHER" = "azure_monitor" ];
    then
        sleep 5 # wait a bit for the exporters to start
        systemctl start moneo_publisher.service 
    else
        echo "Error: Publisher type $PUBLISHER and/or Moneo path $MONEO_PATH not recognized "
        echo "Some services may have started use the stop_moneo_services script to perform a clean stop"
    fi
fi
