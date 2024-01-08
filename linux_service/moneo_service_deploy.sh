#!/bin/bash
########################################################
# This script will configure, install, and launch Moneo services
# with Azure Managed Prometheus Remote Write.
# This script will install the specified release version in the 
# specified directory below
########################################################

MONEO_VERSION=v0.3.4 # Release tag
MONITOR_DIR=/opt/azurehpc/tools # install directory
IDENTITY_CLIENT_ID="38b84eb5-8aec-4971-aaeb-ddd7e9bfef98" # This is the client ID of the Managed Identity for the Azure Prometheus Monitor Workspace
INGESTION_ENDPOINT="https://moneo-amw-q14z.southcentralus-1.metrics.ingest.monitor.azure.com/dataCollectionRules/dcr-c0192b4cd2c748f88ffd422e7a0d77ac/streams/Microsoft-PrometheusMetrics/api/v1/write?api-version=2023-04-24" # This is the ingestion endpoint for the Azure Prometheus Monitor Workspace
MONEO_PATH=$MONITOR_DIR/Moneo
PublisherMethod="" # This is the publisher method for Moneo. Options are azure_monitor, geneva (Msft internal Use), or leave blank for Azure Managed Prometheus

# clone source to specified directory
if [[ -d "$MONEO_PATH" ]]; then
    pushd $MONEO_PATH 
        git config --global --add safe.directory /opt/azurehpc/tools/Moneo
        current_release=$(git describe --tags)
    popd
    if [[ "$current_release" != "$MONEO_VERSION" ]]; then
        pushd $MONITOR_DIR
            echo "Moneo Found but not at Release $MONEO_VERSION. Cloning Moneo $MONEO_VERSION."
            rm -rf Moneo
            git clone https://github.com/Azure/Moneo --branch $MONEO_VERSION
        popd
    fi
else
    pushd $MONITOR_DIR
        echo "Cloning Moneo."
        git clone https://github.com/Azure/Moneo --branch $MONEO_VERSION
    popd
fi

sudo chmod -R 777 $MONEO_PATH

# Configure step
echo "{
    \"IDENTITY_CLIENT_ID\": \"$IDENTITY_CLIENT_ID\",
    \"INGESTION_ENDPOINT\":  \"$INGESTION_ENDPOINT\" }" > $MONEO_PATH/src/worker/publisher/config/managed_prom_config.json

pushd $MONEO_PATH/linux_service
    sudo ./configure_service.sh >> moneoServiceInstall.log
    echo "Moneo install complete"   
    # Start Moneo services
    sudo ./start_moneo_services.sh $PublisherMethod
popd
