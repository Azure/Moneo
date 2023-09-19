# Geneva Agent User Guide #

## Description ##

This guide will walk you through how to share your exporter metrics with Azure using the Geneva Agent.
Note: Currently this feature is private preview and is turned off by default. As of now only internal Microsoft Azure subscriptions are whitelisted, and we recommend you use azure monitor instead, Detailed please refer to this doc: [Azure Monitor Agent](AzureMonitorAgent.md)

## Prequisites ##

1. Prepare Authentication for geneva agent:

    a. User Managed Identity (umi)
    - Create a umi on azure portal, register umi object id on geneva portal with a metricsPublisher role, and add the Moneo service princple to the VM/VMSS
    - Navigate to your VM/VMSS resource on the portal.
    - From the left menu select "identity" ![image](https://user-images.githubusercontent.com/70273488/227347854-89a1fbaa-d9ca-4694-97fa-cac2fd59ea6f.png)
    - From the top tabs select "User assigned"
    - Then click on "Add" this will open a blade to search for the managed identities.
    - search and select "moneo-umi".
    - Click add at the bottom of the open blade.

    b. Certificate (cert)
    - Create Private key pem and public key pem files by:

      ```bash
      openssl genrsa 2048 > mdm-key.pem
      openssl req -x509 -new -key gcskey.pem -out mdm-cert.pem
      ```

    - Print out and get the certicate thumbprint:

      ```
      openssl x509 -in mdm-cert.pem -noout -sha1 -fingerprint
      ```

    - Replace above key-cert pairs with `src/worker/publisher/config/mdm-key.pem` and `src/worker/publisher/config/mdm-cert.pem`
    - Register the thumbprint on geneva portal with a metricsPublisher role.
2. Currently the only supported OS's are Ubuntu 20.04+ and Mariner.
3. python3-dev installed on all nodes.
4. PSSH installed on manager nodes.
5. Ensure passwordless ssh is installed in you environment.

## Steps ##

1. Ensure that all prequisites are met.
2. deploy Moneo
    - Full deployment with umi auth:
   ```python3 moneo.py -d full -g geneva -a umi -c ~/hostfile --manager_host localhost```
    - Worker deployment with cert auth:
   ```python3 moneo.py -d workers -g geneva -a cert -c ~/hostfile```
  
    Note: if install step has already been performed you can use the `-w` flag to skip it.

3. Verify that the exporters and publisher are running with ```ps -eaf | grep python3```
    ![image](https://user-images.githubusercontent.com/70273488/227356884-df1fbc1d-40d1-445c-95c8-756c93df5c10.png)

4. At this point the exporters and publisher shoud be working.

5. Check with Geneva dashboards to verify that the metrics are being ingested.
