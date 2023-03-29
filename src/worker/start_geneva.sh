#!/bin/bash

ConfigFile="${1}"
CONTAINER_NAME="genevamdmagent"

# check if the docker container is running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Geneva Docker is running"
    exit 0
fi

# Config Geneva Metrics Extension(MA)
GENEVA_ACCOUNT_NAME=$(jq -r '.AccountName' $ConfigFile)
GENEVA_MDM_ENDPOINT=$(jq -r '.MDMEndPoint' $ConfigFile)
GENEVA_UMI_OBJECT_ID=$(jq -r '.UmiObjectId' $ConfigFile)

CUR_DIR=$(pwd)
GENEVA_DIR=$CUR_DIR'/etc/geneva'
GENEVA_UMI_DIR=$GENEVA_DIR'/auth_umi.json'

rm -rf $GENEVA_DIR
mkdir -p $GENEVA_DIR
echo "GENEVA_DIR: $GENEVA_DIR"

cat > $GENEVA_UMI_DIR << EOF
{
  "imdsInfo": [{
    "account": "$GENEVA_ACCOUNT_NAME",
    "objectId": "$GENEVA_UMI_OBJECT_ID"
  }]
}
EOF

# Set Geneva Metrics Extension(MA) endpoint
if [[ "$GENEVA_MDM_ENDPOINT" == *"ppe"* ]]; then
  METRIC_ENDPOINT="https://global.ppe.microsoftmetrics.com/"
elif [[ $str == *"prod"* ]]; then
  METRIC_ENDPOINT="https://global.prod.microsoftmetrics.com/"
else
    echo "Invalid Geneva Metrics Extension(MA) Endpoint"
    exit 1
fi



# Run Geneva Metrics Extension(MA) docker container
sudo docker run -d --name=$CONTAINER_NAME --net=host --uts=host                      \
                -v $GENEVA_DIR:/etc/geneva/ -e MDM_ACCOUNT=$GENEVA_ACCOUNT_NAME     \
                -e MDM_INPUT="otlp_grpc,statsd_udp" -e MDM_LOG_LEVEL="info"         \
                -e CONFIG_OVERRIDES_FILE="/etc/geneva/auth_umi.json"                \
                -e METRIC_ENDPOINT=$METRIC_ENDPOINT                                 \
                genevamdm
