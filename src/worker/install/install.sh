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
        # Install open telemetry related packages
        python3 -m pip install opentelemetry-sdk opentelemetry-exporter-otlp
        
        # Pull Geneva Metrics Extension(MA) docker image
        docker pull linuxgeneva-microsoft.azurecr.io/genevamdm:2.2023.316.006-5d91fa-20230316t1622
        docker tag linuxgeneva-microsoft.azurecr.io/genevamdm:2.2023.316.006-5d91fa-20230316t1622 genevamdm
        docker rmi linuxgeneva-microsoft.azurecr.io/genevamdm:2.2023.316.006-5d91fa-20230316t1622
    elif [ $PUBLISHER_INSTALL == 'azure_monitor' ];
    then
        $(dirname "${BASH_SOURCE[0]}")/azure_monitor.sh
    else
        echo "Publisher not supported"
    fi
fi
