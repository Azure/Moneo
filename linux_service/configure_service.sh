#!/bin/bash

MONEO_PATH=$1

if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path $MONEO_PATH does not exist. Ensure you are using the correct arguments  
    (i.e. ./configure_service.sh <Moneo Full Path>, or ./configure_service.sh <Moneo Full Path> true/false). Exiting." 
    exit 1
fi

# replace the moneo path place holder with actaul moneo path and Move service file to systemd directory
sed  "s#<Moneo_Path>#$MONEO_PATH#g" $MONEO_PATH/linux_service/moneo@.service > /etc/systemd/system/moneo@.service

echo "configuring publisher service" 
sed  "s#<Moneo_Path>#$MONEO_PATH#g;" $MONEO_PATH/linux_service/moneo_publisher.service > /etc/systemd/system/moneo_publisher.service

$MONEO_PATH/src/worker/install/install.sh azure_monitor

systemctl daemon-reload
