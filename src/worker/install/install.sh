#!/bin/bash

PUBLISHER_INSTALL=$1
MDM_DOCKER_VERSION=2.2023.316.006-5d91fa-20230316t1622
DOCKER_IMAGE_ID=7f41d00ddf6a

if [ -e '/dev/nvidiactl' ]; then
# Nvidia
    $(dirname "${BASH_SOURCE[0]}")/nvidia.sh
elif [ -e '/dev/kfd' ];then
# AMD
    $(dirname "${BASH_SOURCE[0]}")/amd.sh
else
	source $(dirname "${BASH_SOURCE[0]}")/common.sh
fi

# uninstall to deal with Azure monitor and Geneva differences
python3 -m pip -qqq uninstall \
azure-monitor-opentelemetry-exporter  \
opentelemetry-instrumentation \
opentelemetry-api \
opentelemetry-sdk \
azure-monitor-opentelemetry \
opentelemetry-exporter-otlp \
opentelemetry-exporter-otlp-proto-grpc \
opentelemetry-exporter-otlp-proto-http \
opentelemetry-instrumentation-django \
opentelemetry-instrumentation-flask \
opentelemetry-instrumentation-requests \
opentelemetry-instrumentation-wsgi \
opentelemetry-instrumentation-dbapi \
opentelemetry-instrumentation-psycopg2 -y

if [ -n "$PUBLISHER_INSTALL" ];
then
    if [ $PUBLISHER_INSTALL == 'geneva' ];
    then
        # Install open telemetry related packages
        python3 -m pip -qqq install opentelemetry-sdk opentelemetry-exporter-otlp
        
        if ! docker images | grep genevamdm | grep -q $DOCKER_IMAGE_ID; then
            # Pull Geneva Metrics Extension(MA) docker image
			docker pull	linuxgeneva-microsoft.azurecr.io/genevamdm:$MDM_DOCKER_VERSION
			docker tag linuxgeneva-microsoft.azurecr.io/genevamdm:$MDM_DOCKER_VERSION genevamdm
			docker rmi linuxgeneva-microsoft.azurecr.io/genevamdm:$MDM_DOCKER_VERSION
        fi
    elif [ $PUBLISHER_INSTALL == 'azure_monitor' ];
    then
        $(dirname "${BASH_SOURCE[0]}")/azure_monitor.sh
    else
        echo "Publisher not supported"
    fi
fi
