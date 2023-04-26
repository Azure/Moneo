#!/bin/bash

get_cluster_name(){
    cluster_name=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/name?api-version=2021-02-01&format=text" | cut -d'_' -f1)

    echo $cluster_name
}

WORK_DIR=/tmp/moneo-master
SIDECAR_CONFIG=$WORK_DIR/'sidecar_config.json'
SIDECAR_VERSION='prom-remotewrite-20230323.1'
SIDERCAR_DOCKER='mcr.microsoft.com/azuremonitor/prometheus/promdev/prom-remotewrite:'$SIDECAR_VERSION

CLUSTER_NAME=$(get_cluster_name)
IDENTITY_CLIENT_ID=$(jq -r '.IDENTITY_CLIENT_ID' $SIDECAR_CONFIG)
INGESTION_ENDPOINT=$(jq -r '.INGESTION_ENDPOINT' $SIDECAR_CONFIG)

echo "CLUSTER_NAME: $CLUSTER_NAME"
echo "IDENTITY_CLIENT_ID: $IDENTITY_CLIENT_ID"
echo "INGESTION_ENDPOINT: $INGESTION_ENDPOINT"
echo "SIDERCAR_DOCKER: $SIDERCAR_DOCKER"
# pull sidecar image
docker pull $SIDERCAR_DOCKER
docker tag  $SIDERCAR_DOCKER prometheus_sidecar
docker rmi  $SIDERCAR_DOCKER

# start sidecar container
docker rm -f prometheus_sidecar || true
sudo docker run --name=prometheus_sidecar \
    -it --net=host --uts=host -d \
    -e CLUSTER=$CLUSTER_NAME -e LISTENING_PORT=8081 \
    -e IDENTITY_TYPE=userAssigned -e AZURE_CLIENT_ID=$IDENTITY_CLIENT_ID \
    -e INGESTION_URL=$INGESTION_ENDPOINT prometheus_sidecar
