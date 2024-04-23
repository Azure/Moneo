#!/bin/bash

INSTANCE_NAME=$(hostname)
WORK_DIR="${1:-/tmp/moneo-worker}"
PROM_CONFIG=$WORK_DIR/prometheus.yml
CONFIG_DIR=$WORK_DIR
MANAGED_PROM_CONFIG=$CONFIG_DIR/moneo_config.json

get_subscription(){
    subscription_name=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/subscriptionId?api-version=2021-02-01&format=text")

    echo $subscription_name
}

get_cluster_name(){
    cluster_name=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance/compute/name?api-version=2021-02-01&format=text" | cut -d'_' -f1)

    echo $cluster_name
}

get_physical_host_name(){
    KVP_PATH='/opt/azurehpc/tools/kvp_client'
    if [ -f "$KVP_PATH" ]; then
        HOST_NAME=$("$KVP_PATH" 3 | grep -i 'PhysicalHostName;' | awk -F 'Value:'  '{print $2}');
        echo $HOST_NAME
    else
        echo "physical_host_name"
    fi
}

SUBSCRIPTION_NAME=$(get_subscription)
CLUSTER_NAME=$(get_cluster_name)
PHYS_HOST_NAME=$(get_physical_host_name)

IDENTITY_CLIENT_ID=$(jq -r '.prom_config.IDENTITY_CLIENT_ID' $MANAGED_PROM_CONFIG)
INGESTION_ENDPOINT=$(jq -r '.prom_config.INGESTION_ENDPOINT' $MANAGED_PROM_CONFIG)

generate_prom(){
    DCMG_TARGET="        - $INSTANCE_NAME:8000\n"
    NET_TARRGET="        - $INSTANCE_NAME:8001\n"
    NODE_TARGET="        - $INSTANCE_NAME:8002\n"
    CUST_TARGET="        - $INSTANCE_NAME:8003\n"

    #replace placeholder
    sed -i -r "s/subscription_id/$SUBSCRIPTION_NAME/" $PROM_CONFIG
    sed -i -r "s/cluster_name/$CLUSTER_NAME/" $PROM_CONFIG
    sed -i -r "s/instance_name/$INSTANCE_NAME/" $PROM_CONFIG
    sed -i -r "s/physical_host_name/$PHYS_HOST_NAME/" $PROM_CONFIG
    sed -i -r "s@ingestion_endpoint@$INGESTION_ENDPOINT@" $PROM_CONFIG
    sed -i -r "s/identity_client_id/$IDENTITY_CLIENT_ID/" $PROM_CONFIG

    sed -i -r "s/\s+- moneo-worker-0:8000/$DCMG_TARGET/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8001/$NET_TARRGET/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8002/$NODE_TARGET/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8003/$CUST_TARGET/" $PROM_CONFIG
}

# generate prometheus config
generate_prom

# start prometheus container
mkdir -m 777 /mnt/prometheus
docker rm -f prometheus || true
docker run --name prometheus \
    -it --net=host -d -p 9090:9090 \
    --restart=unless-stopped       \
    -v /mnt/prometheus:/prometheus \
    -v $PROM_CONFIG:/etc/prometheus/prometheus.yml \
    prom/prometheus \
    --storage.tsdb.path=/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.enable-admin-api

echo "SUBSCRIPTION_NAME: $SUBSCRIPTION_NAME"
echo "CLUSTER_NAME: $CLUSTER_NAME"
echo "INSTANCE_NAME: $INSTANCE_NAME"
echo "PHYS_HOST_NAME: $PHYS_HOST_NAME"

echo "IDENTITY_CLIENT_ID: $IDENTITY_CLIENT_ID"
echo "INGESTION_ENDPOINT: $INGESTION_ENDPOINT"
