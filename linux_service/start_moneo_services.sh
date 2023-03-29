#!/bin/bash
PUBLISHER=$1

systemctl start moneo@node_exporter.service
systemctl start moneo@net_exporter.service
systemctl start moneo@nvidia_exporter.service

if [[ ! -z "$PUBLISHER" ]];
then
    if [[ "$PUBLISHER" = true ]];
    then
        sleep 5 # wait a bit for the exporters to start
        systemctl start moneo_publisher.service 
    fi
fi
