#!/bin/bash

MONEO_PATH=$1


if [[ -z "$MONEO_PATH" ]];
then
    MONEO_PATH=/opt/azurehpc/tools/Moneo
    echo 'default Moneo path used'
fi

# replace the moneo path place holder with actaul moneo path and Move service file to systemd directory
sed  "s#<Moneo_Path>#$MONEO_PATH#g" $MONEO_PATH/linux_service/moneo@.service > /etc/systemd/system/moneo@.service


sed  "s#<Moneo_Path>#$MONEO_PATH#g" $MONEO_PATH/linux_service/moneo_publisher.service > /etc/systemd/system/moneo_publisher.service

systemctl daemon-reload

# enable exporter services
systemctl enable moneo@node_exporter.service
systemctl enable moneo@net_exporter.service
systemctl enable moneo@nvidia_exporter.service
systemctl enable moneo_publisher.service