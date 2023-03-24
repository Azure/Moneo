#!/bin/bash

ConfigFile="${1}"

# Ensure that https transport for apt and gnupg are installed
sudo apt-get update
sudo apt-get install -y apt-transport-https gnupg

# Accept Microsoft public keys
wget -qO - https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
wget -qO - https://packages.microsoft.com/keys/msopentech.asc | sudo apt-key add -

# Source information on OS distro and code name
. /etc/os-release
ARCHITECTURE=$(dpkg --print-architecture)

if [ "$ID" = ubuntu ]; then
    # this has also to be arm64
    if [[ "$ARCHITECTURE" = arm64 ]] && [[ "$VERSION_CODENAME" = bionic || "$VERSION_CODENAME" = xenial ]]; then
        REPO_NAME=azurecore-multiarch
    else
        REPO_NAME=azurecore
    fi
elif [ "$ID" = debian ]; then
    REPO_NAME=azurecore-debian
else
    echo "Unsupported distribution: $ID"
    exit 1
fi

# Add azurecore repo and update package list
echo "deb [arch=$ARCHITECTURE] https://packages.microsoft.com/repos/$REPO_NAME $VERSION_CODENAME main" | sudo tee -a /etc/apt/sources.list.d/azure.list
sudo apt-get update

# Install MetricsExtension
sudo apt-get install -y metricsext2

# Config Geneva Metrics Extension(MA)
GENEVA_ACCOUNT_NAME=$(jq -r '.AccountName' $ConfigFile)
GENEVA_MDM_ENDPOINT=$(jq -r '.MDMEndPoint' $ConfigFile)
GENEVA_UMI_OBJECT_ID=$(jq -r '.UmiObjectId' $ConfigFile)

GENEVA_DIR='/etc/geneva'
GENEVA_UMI_DIR=$GENEVA_DIR'/auth_umi.json'
rm -rf $GENEVA_DIR
mkdir -p $GENEVA_DIR

cat > $GENEVA_UMI_DIR << EOF
{
  "imdsInfo": [{
    "account": "$GENEVA_ACCOUNT_NAME",
    "objectId": "$GENEVA_UMI_OBJECT_ID"
  }]
}
EOF

cat /etc/default/mdm \
  | sed "s#<MDMEndPoint>#$GENEVA_MDM_ENDPOINT#" \
  | sed "s#-MonitoringAccount <Account>##" \
  | sed "s# -CertFile <FullPath-PublicCert.pem> -PrivateKeyFile <FullPath-PrivateKey.pem># -Input otlp_grpc,statsd_udp -ConfigOverridesFilePath $GENEVA_UMI_DIR#" \
  | sudo tee /etc/default/mdm

# Start Geneva Metrics Extension(MA)
sudo systemctl enable mdm
sudo systemctl start mdm
