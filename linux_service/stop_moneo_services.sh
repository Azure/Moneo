#!/bin/bash

systemctl stop moneo@node_exporter.service
systemctl stop moneo@net_exporter.service
systemctl stop moneo@nvidia_exporter.service
systemctl stop moneo_publisher.service

systemctl disable moneo@node_exporter.service
systemctl disable moneo@net_exporter.service
systemctl disable moneo@nvidia_exporter.service
systemctl disable moneo_publisher.service

if [[ $(docker ps -a | grep genevamdmagent) ]]; then
    echo "Stopping Geneva Metrics Extension(MA) container"
    docker stop genevamdmagent
    docker rm genevamdmagent
fi