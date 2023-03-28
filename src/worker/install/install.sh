#!/bin/bash
arch="nvidia"

PUBLISHER_INSTALL=$1

if [ -e '/dev/nvidiactl' ]; then
# Nvidia
    $(dirname "${BASH_SOURCE[0]}")/nvidia.sh
elif [ -e '/dev/kfd' ];then
# AMD
    $(dirname "${BASH_SOURCE[0]}")/amd.sh
else
	source $(dirname "${BASH_SOURCE[0]}")/common.sh
fi

python3 -m pip uninstall opentelemetry-sdk azure-monitor-opentelemetry opentelemetry-exporter-otlp -y

if [ -n "$PUBLISHER_INSTALL" ];
then
    if [ $PUBLISHER_INSTALL == 'geneva' ];
    then
        $(dirname "${BASH_SOURCE[0]}")/geneva.sh  $(dirname "${BASH_SOURCE[0]}")/config/geneva_config.json
    elif [ $PUBLISHER_INSTALL == 'azure_monitor' ];
    then
        $(dirname "${BASH_SOURCE[0]}")/azure_monitor.sh
    else
        echo "Publisher not supported"
    fi
fi
