#!/bin/bash

MONEO_PATH=/opt/azurehpc/tools/Moneo

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path $MONEO_PATH does not exist. Ensure you have Moneo directory in this path $MONEO_PATH"
    exit 1
fi

# replace the moneo path place holder with actaul moneo path and Move service file to systemd directory
sed  "s#<Moneo_Path>#$MONEO_PATH#g" $MONEO_PATH/linux_service/moneo@.service > /etc/systemd/system/moneo@.service

echo "configuring publisher service" 
sed  "s#<Moneo_Path>#$MONEO_PATH#g;" $MONEO_PATH/linux_service/moneo_publisher.service > /etc/systemd/system/moneo_publisher.service

$MONEO_PATH/src/worker/install/install.sh azure_monitor

systemctl daemon-reload
