#!/bin/bash

INSTANCE_NAME=$(hostname)
WORK_DIR=/tmp/moneo-worker
PROM_CONFIG=$WORK_DIR/prometheus.yml
CONFIG_DIR=$WORK_DIR/publisher/config
PROM_SIDECAR_CONFIG=$CONFIG_DIR/prom_sidecar_config.json
SIDECAR_VERSION='prom-remotewrite-20230323.1'
SIDERCAR_DOCKER='mcr.microsoft.com/azuremonitor/prometheus/promdev/prom-remotewrite:'$SIDECAR_VERSION

get_subscription(){
    subscription_name=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/subscriptionId?api-version=2021-02-01&format=text")

    echo $subscription_name
}

get_cluster_name(){
    cluster_name=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/name?api-version=2021-02-01&format=text" | cut -d'_' -f1)

    echo $cluster_name
}

SUBSCRIPTION_NAME=$(get_subscription)
CLUSTER_NAME=$(get_cluster_name)

generate_prom(){
    DCMG_TARGET="        - $INSTANCE_NAME:8000\n"
    NET_TARRGET="        - $INSTANCE_NAME:8001\n"
    NODE_TARGET="        - $INSTANCE_NAME:8002\n"

    #replace placeholder
    sed -i -r "s/subscription_id/$SUBSCRIPTION_NAME/" $PROM_CONFIG
    sed -i -r "s/cluster_name/$CLUSTER_NAME/" $PROM_CONFIG
    sed -i -r "s/instance_name/$INSTANCE_NAME/" $PROM_CONFIG

    sed -i -r "s/\s+- moneo-worker-0:8000/$DCMG_TARGET/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8001/$NET_TARRGET/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8002/$NODE_TARGET/" $PROM_CONFIG
}

# generate prometheus config
generate_prom

# start prometheus container
mkdir -m 777 /mnt/prometheus
docker rm -f prometheus || true
docker run --name prometheus \
    -it --net=host -d -p 9090:9090 \
    -v /mnt/prometheus:/prometheus \
    -v $PROM_CONFIG:/etc/prometheus/prometheus.yml \
    prom/prometheus \
    --storage.tsdb.path=/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.enable-admin-api

# get prom sidecar config
IDENTITY_CLIENT_ID=$(jq -r '.IDENTITY_CLIENT_ID' $PROM_SIDECAR_CONFIG)
INGESTION_ENDPOINT=$(jq -r '.INGESTION_ENDPOINT' $PROM_SIDECAR_CONFIG)

echo "SUBSCRIPTION_NAME: $SUBSCRIPTION_NAME"
echo "CLUSTER_NAME: $CLUSTER_NAME"
echo "INSTANCE_NAME: $INSTANCE_NAME"

echo "IDENTITY_CLIENT_ID: $IDENTITY_CLIENT_ID"
echo "INGESTION_ENDPOINT: $INGESTION_ENDPOINT"
echo "SIDERCAR_DOCKER: $SIDERCAR_DOCKER"

# pull prom sidecar image
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
