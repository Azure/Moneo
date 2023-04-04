#!/bin/bash

AUTH="${1}"
CONFIG="${2}"
CONTAINER_NAME="genevamdmagent"

GENEVA_CONFIG=$CONFIG/geneva_config.json
# check if the docker container is running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Geneva Docker is running"
    exit 0
fi

GENEVA_ACCOUNT_NAME=$(jq -r '.AccountName' $GENEVA_CONFIG)
GENEVA_MDM_ENDPOINT=$(jq -r '.MDMEndPoint' $GENEVA_CONFIG)

# Set Geneva Metrics Extension(MA) endpoint
if [[ "$GENEVA_MDM_ENDPOINT" == *"ppe"* ]]; then
  METRIC_ENDPOINT="https://global.ppe.microsoftmetrics.com/"
elif [[ $str == *"prod"* ]]; then
  METRIC_ENDPOINT="https://global.prod.microsoftmetrics.com/"
else
    echo "Invalid Geneva Metrics Extension(MA) Endpoint"
    exit 1
fi

CUR_DIR=$(pwd)
GENEVA_DIR=$CUR_DIR'/etc/geneva'
rm -rf $GENEVA_DIR
mkdir -p $GENEVA_DIR
echo "GENEVA_DIR: $GENEVA_DIR"

if [ $AUTH == "umi" ];
then
    GENEVA_UMI_OBJECT_ID=$(jq -r '.UmiObjectId' $GENEVA_CONFIG)
    GENEVA_UMI_DIR=$GENEVA_DIR'/auth_umi.json'

cat > $GENEVA_UMI_DIR << EOF
{
  "imdsInfo": [{
    "account": "$GENEVA_ACCOUNT_NAME",
    "objectId": "$GENEVA_UMI_OBJECT_ID"
  }]
}
EOF

    # Run Geneva Metrics Extension(MA) docker container
    sudo docker run -d --name=$CONTAINER_NAME --net=host --uts=host                     \
                    -v $GENEVA_DIR:/etc/geneva/ -e MDM_ACCOUNT=$GENEVA_ACCOUNT_NAME     \
                    -e MDM_INPUT="otlp_grpc,statsd_udp" -e MDM_LOG_LEVEL="info"         \
                    -e CONFIG_OVERRIDES_FILE="/etc/geneva/auth_umi.json"                \
                    -e METRIC_ENDPOINT=$METRIC_ENDPOINT                                 \
                    genevamdm
elif [ $AUTH == "cert" ];
then
    MDM_KEY=$CONFIG/mdm-key.pem
    MDM_CERT=$CONFIG/mdm-cert.pem
    cp $MDM_KEY $GENEVA_DIR
    cp $MDM_CERT $GENEVA_DIR
    chmod 600 $GENEVA_DIR/mdm-key.pem
    chmod 600 $GENEVA_DIR/mdm-cert.pem

    # Run Geneva Metrics Extension(MA) docker container
    sudo docker run -d --name=$CONTAINER_NAME --net=host --uts=host                     \
                    -v $GENEVA_DIR:/tmp/geneva_mdm -e MDM_ACCOUNT=$GENEVA_ACCOUNT_NAME  \
                    -e MDM_INPUT="otlp_grpc,statsd_udp" -e MDM_LOG_LEVEL="info"         \
                    -e METRIC_ENDPOINT=$METRIC_ENDPOINT                                 \
                    genevamdm
else
    # Unsupported auth type
    echo "Publisher auth not supported"
fi

# Run Geneva Metrics Extension(MA) docker container
sudo docker run -d --name=$CONTAINER_NAME --net=host --uts=host                      \
                -v $GENEVA_DIR:/etc/geneva/ -e MDM_ACCOUNT=$GENEVA_ACCOUNT_NAME     \
                -e MDM_INPUT="otlp_grpc,statsd_udp" -e MDM_LOG_LEVEL="info"         \
                -e CONFIG_OVERRIDES_FILE="/etc/geneva/auth_umi.json"                \
                -e METRIC_ENDPOINT=$METRIC_ENDPOINT                                 \
                genevamdm
