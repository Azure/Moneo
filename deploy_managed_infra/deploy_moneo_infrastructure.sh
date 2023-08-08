#!/bin/bash

function check_output(){
  output=$1
  if [ $output != 0 ]; then
    echo "The identity asignment encountered an error. Please review the error and fix the issues"
    exit 1
  fi
}


if az account show &>/dev/null; then
  # You are logged in
  echo "You are logged in to the Azure CLI."
  # Add other commands you want to run when logged in
else
  # You are not logged in
  echo "You are not logged in to the Azure CLI. Please run 'az login' to log in."
  # Add other commands or actions you want to take when not logged in
  exit 1
fi

# Change the naming if desired
prometheus_mon_workspace="moneo-amw"
rgroup="moneo-rg" 
idname="moneo-identity"
grafana_name="moneo-dashboard"

# change location and subscription
alert_email="<email>"
location="southcentralus"
subid="<sub-id>"

az account set --subscription $subid

az group create --name $rgroup --location $location

az deployment group create \
  --name moneoInfraDeploy \
  --resource-group $rgroup \
  --template-file managed_infra_template.json \
  --parameters  accounts_moneo_amw_name=$prometheus_mon_workspace \
  --parameters  grafana_moneo_grafana_name=$grafana_name \
  --parameters userAssignedIdentities_moneo_identity_name=$idname \
  --parameters moeno_location=$location \
  --parameters alert_email=$alert_email \
  --verbose

if [ $? -eq 0 ]; then
    echo "The deployment command completed successfully. Moving on to identity asignment"
else
    echo "The deployment command encountered an error. Please review the error and fix the issues"
    exit 1
fi

# Get the Object ID of the Managed Identity
managedIdentityObjectId=$(az identity show -n $idname -g $rgroup --subscription $subid --query principalId -o tsv)
dataCollectionEndpointResourceId=$(az monitor account show  -n $prometheus_mon_workspace -g  $rgroup  --subscription $subid --query "defaultIngestionSettings.dataCollectionEndpointResourceId")
dataCollectionRuleResourceId=$(az monitor account show  -n $prometheus_mon_workspace -g  $rgroup  --subscription $subid --query "defaultIngestionSettings.dataCollectionRuleResourceId")
dataCollectionEndpointResourceId=$(echo "$dataCollectionEndpointResourceId" | sed 's/"//g')
dataCollectionRuleResourceId=$(echo "$dataCollectionRuleResourceId" | sed 's/"//g')
prom_work_space="/subscriptions/$subid/resourceGroups/$rgroup/providers/microsoft.monitor/accounts/$prometheus_mon_workspace"
grafana_id="/subscriptions/$subid/resourceGroups/$rgroup/providers/Microsoft.Dashboard/grafana/$grafana_name"
grafobjectid=$(az resource show --ids $grafana_id --query "identity.principalId" --output tsv)

# Assign "Monitoring Metrics Publisher" role to the Managed Identity for Data Collection Endpoint
az role assignment create --role "Monitoring Metrics Publisher" --assignee-object-id $managedIdentityObjectId --scope $dataCollectionEndpointResourceId --subscription $subid

check_output $?

# Assign "Monitoring Metrics Publisher" role to the Managed Identity for Data Collection Rule
az role assignment create --role "Monitoring Metrics Publisher" --assignee-object-id $managedIdentityObjectId --scope $dataCollectionRuleResourceId --subscription $subid

check_output $?

# Assign "Monitoring Metrics Publisher" role to the Managed Identity for Azure monitor workspace
az role assignment create --role "Monitoring Metrics Publisher" --assignee-object-id $managedIdentityObjectId --scope $prom_work_space

check_output $?

az role assignment create --role "Monitoring Reader" --assignee-object-id $grafobjectid --scope $prom_work_space

check_output $?

echo "The identity asignment completed successfully. Setup is complete."

exit 0
