#!/bin/bash
echo "Stopping Exporters Services"

sudo systemctl stop moneo@node_exporter.service 2> /dev/null
sudo systemctl stop moneo@net_exporter.service 2> /dev/null
sudo systemctl stop moneo@nvidia_exporter.service 2> /dev/null
sudo systemctl stop moneo_publisher.service 2> /dev/null

sudo systemctl disable moneo@node_exporter.service 2> /dev/null
sudo systemctl disable moneo@net_exporter.service 2> /dev/null
sudo systemctl disable moneo@nvidia_exporter.service 2> /dev/null
sudo systemctl disable moneo_publisher.service 2> /dev/null

if [[ $(sudo docker ps -a | grep prometheus) ]]; then
    echo "Stopping Prometheus containers"
    sudo docker stop prometheus genevamdmagent 2> /dev/null
    sudo docker rm prometheus genevamdmagent 2> /dev/null
elif [[ $(sudo docker ps -a | grep genevamdmagent) ]]; then
    echo "Stopping Geneva containers"
    sudo docker stop genevamdmagent 2> /dev/null
    sudo docker rm genevamdmagent 2> /dev/null
fi
