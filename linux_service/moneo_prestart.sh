#!/bin/bash

MONEO_PATH=$1

# check MONEO_PATH variable is set if not set to default
if [[ -z "$MONEO_PATH" ]];
then
    MONEO_PATH=/opt/azurehpc/tools/Moneo
    echo 'default Moneo path used'
fi
echo "Moneo path=$MONEO_PATH"

# check that the path provided exists
if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path does not exist. Please install Moneo or provide path to this script. Exiting prestart script"
    exit 1
fi

# check/create the working director exists
mkdir -p /tmp/moneo-worker

cp -rf $MONEO_PATH/src/worker/* /tmp/moneo-worker/
cp -f $MONEO_PATH/moneo_config.json /tmp/moneo-worker/
