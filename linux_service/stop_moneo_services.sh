#!/bin/bash

systemctl stop moneo@node_exporter.service
systemctl stop moneo@net_exporter.service
systemctl stop moneo@nvidia_exporter.service
systemctl stop moneo_publisher.service

systemctl disable moneo@node_exporter.service
systemctl disable moneo@net_exporter.service
systemctl disable moneo@nvidia_exporter.service
systemctl disable moneo_publisher.service

if [[ $(docker ps -a | grep prometheus_sidecar) ||  $(docker ps -a | grep prometheus) ]]; then
    echo "Stopping Prometheus containers"
    docker stop prometheus_sidecar
    docker rm prometheus_sidecar
    docker stop prometheus
    docker rm prometheus
fi
