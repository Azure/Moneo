#!/bin/bash

MONEO_PATH=$1
EXE_TYPE=$2

# check MONEO_PATH variable is set if not set to default
if [[ -z "$MONEO_PATH" ]];
then
    MONEO_PATH=/opt/azurehpc/tools/Moneo
    echo 'default Moneo path used'
fi
echo "Moneo path=$MONEO_PATH"

if [[ -z "$EXE_TYPE" ]];
then
    echo 'Error: No executable passed in. Exiting prestart script.'
    exit 1
fi

# check that the path provided exists
if [[ ! -d "$MONEO_PATH" ]];
then
    echo "Error: Moneo path does not exist. Please install Moneo or provide path to this script. Exiting prestart script"
    exit 1
fi

# check/create the working director exists
mkdir -p /tmp/moneo-worker/exporters
mkdir -p /tmp/moneo-worker/publisher

# copy exporters or publisher
if [[ "metrics_publisher.py" == "$EXE_TYPE"  ]];
then
    if [[ ! -e "$MONEO_PATH/src/worker/publisher/$EXE_TYPE" ]];
    then
        echo "$MONEO_PATH/src/worker/publisher/$EXE_TYPE Does not exist"
        exit 1
    fi
    cp $MONEO_PATH/src/worker/publisher/$EXE_TYPE  /tmp/moneo-worker/publisher/
else
    if [[ ! -e "$MONEO_PATH/src/worker/exporters/$EXE_TYPE" ]];
    then
        echo "Error: $MONEO_PATH/src/worker/exporters/$EXE_TYPE Does not exist. Exiting prestart script"
        exit 1
    fi
    cp $MONEO_PATH/src/worker/exporters/$EXE_TYPE  /tmp/moneo-worker/exporters/
fi

# needed for node exporter
if [[ "node_exporter.py" == "$EXE_TYPE"  ]];
then
    cp $MONEO_PATH/src/worker/exporters/base_exporter.py  /tmp/moneo-worker/exporters/
fi
