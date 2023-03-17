#!/bin/bash

IMAGE=azmoneo/moneo-exporter:nvidia
CONT_NAME=moneo-exporter-nvidia
PROFILING=$1

if [ -e "/dev/nvidiactl" ]; then
    docker pull $IMAGE

    docker rm --force $CONT_NAME && \
    docker run --name=$CONT_NAME --net=host \
        -e PROFILING=$PROFILING --rm --runtime=nvidia \
        --cap-add SYS_ADMIN -v /sys:/hostsys/ -itd $IMAGE
else

echo 'No Nvidia devices found Docker deployment canceled'

fi
