#!/bin/bash
########################################################
# This script will configure, install, and launch Moneo services
# with Azure Managed Prometheus Remote Write.
# This script will install the specified release version in the 
# specified directory below
########################################################

MONEO_VERSION=v0.3.4 # Release tag
MONITOR_DIR=/opt/azurehpc/tools # install directory
IDENTITY_CLIENT_ID="" # This is the client ID of the Managed Identity for the Azure Prometheus Monitor Workspace
INGESTION_ENDPOINT=""
PublisherMethod="" # This is the publisher method for Moneo. Options are azure_monitor, geneva (Msft internal Use), or leave blank for Azure Managed Prometheus
MONEO_PATH=$MONITOR_DIR/Moneo
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
jq '(.prom_config.IDENTITY_CLIENT_ID |= "'"$IDENTITY_CLIENT_ID"'")' "$MONEO_PATH/moneo_config.json" > "$MONEO_PATH/temp.json" && mv "$MONEO_PATH/temp.json" "$MONEO_PATH/moneo_config.json"
jq '(.prom_config.INGESTION_ENDPOINT |= "'"$INGESTION_ENDPOINT"'")' "$MONEO_PATH/moneo_config.json" > "$MONEO_PATH/temp.json" && mv "$MONEO_PATH/temp.json" "$MONEO_PATH/moneo_config.json"
rm -f "$MONEO_PATH/temp.json"

pushd $MONEO_PATH/linux_service
    sudo ./configure_service.sh >> moneoServiceInstall.log
    echo "Moneo install complete"   
    # Start Moneo services
    sudo ./start_moneo_services.sh $PublisherMethod
popd
