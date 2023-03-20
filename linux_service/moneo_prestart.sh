#!/bin/bash

MONEO_PATH=$1
EXE_TYPE=$2

if [[ -e "/tmp/moneo-worker/$EXE_TYPE" ]];
then
    echo "no set up needed"
    exit 0
fi
# executable does not exist


if [[ -z "$MONEO_PATH" ]];
then
    MONEO_PATH=/opt/azurehpc/tools/Moneo
    echo 'default Moneo path used'
fi

echo "Moneo path=$MONEO_PATH"

if [[ -d "$MONEO_PATH" ]];
then
    :
else
    echo "Moneo path does not exist. Please insatll Moneo or provide path to this script."
fi

if [ -d "/tmp/moneo-worker" ];
then
    echo 'Moneo worker directory exists'

else
    mkdir -p /tmp/moneo-worker/exporters
fi

cp $MONEO_PATH/src/worker/exporters/$EXE_TYPE  /tmp/moneo-worker/exporters/

if [[ "node_exporter.py" == "$EXE_TYPE"  ]];
then
    cp $MONEO_PATH/src/worker/exporters/base_exporter.py  /tmp/moneo-worker/exporters/
fi
