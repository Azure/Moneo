#!/bin/bash
PUBLISHER=$1
MONEO_PATH=$2

systemctl enable moneo@node_exporter.service
systemctl enable moneo@net_exporter.service
systemctl enable moneo@nvidia_exporter.service

systemctl start moneo@node_exporter.service
systemctl start moneo@net_exporter.service
systemctl start moneo@nvidia_exporter.service

if [[ ! -z "$PUBLISHER" ]];
then
    if [ "$PUBLISHER" = "geneva" ] && [ -d $MONEO_PATH ];
    then
        #starts Geneva agent
        $MONEO_PATH/src/worker/start_geneva.sh cert $MONEO_PATH/src/worker/publisher/config
        sleep 5 # wait a bit for the exporters to start
        systemctl enable moneo_publisher.service
        systemctl start moneo_publisher.service 
    elif [ "$PUBLISHER" = "azure_monitor" ];
    then
        sleep 5 # wait a bit for the exporters to start
        systemctl enable moneo_publisher.service
        systemctl start moneo_publisher.service 
    else
        echo "Either PUBLISHER OR MONEO_PATH unrecognized. PUBLISHER can be geneva or azure_monitor. If publisher is geneva MONEO_PATH must be defined."
        echo "Some services may have started use the stop_moneo_services script to perform a clean stop"
    fi
fi
