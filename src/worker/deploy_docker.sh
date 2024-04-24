#!/bin/bash

IMAGE=azmoneo/moneo-exporter:nvidia
CONT_NAME=moneo-exporter-nvidia

if [ -e "/dev/nvidiactl" ]; then
    docker pull $IMAGE

    docker rm --force $CONT_NAME && \
    docker run --name=$CONT_NAME --net=host --restart=unless-stopped \
        --rm --runtime=nvidia \
        --cap-add SYS_ADMIN -v /sys:/hostsys/ -v /tmp/moneo-worker/moneo_config.json:/tmp/moneo-worker/moneo_config.json -itd $IMAGE
else

echo 'No Nvidia devices found Docker deployment canceled'

fi
