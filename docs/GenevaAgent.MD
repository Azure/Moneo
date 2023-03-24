Geneva Agent User Guide
=====
Description
-----
This guide will walk you through how to share your exporter metrics with Azure using the Geneva Agent.
Note: Currently this feature is private preview and is turned off by default. As of now only internal Microsoft Azure subscriptions are whitelisted.

Prequisites:
1. Add the Moneo service princple to the VM/VMSS
  - Navigate to your VM/VMSS resource on the portal.
  - From the left menu select "identity" ![image](https://user-images.githubusercontent.com/70273488/227347854-89a1fbaa-d9ca-4694-97fa-cac2fd59ea6f.png)
  - From the top tabs select "User assigned"
  - Then click on "Add" this will open a blade to search for the managed identities.
  - search and select "moneo-umi".
  - Click add at the bottom of the open blade.
2. Currently the only supported OS's are Ubuntu 20.04 and up.
3. python3-dev installed on all nodes.
4. PSSH installed on manager nodes.
5. Ensure passwordless ssh is installed in you environment.
6. 

Steps
-----
1. Ensure that all prequisites are met.
2. deploy Moneo:
  - Full deployment ```python3 moneo.py -d full -g -c ~/hostfile --manager_host localhost```
  - Worker deployment ```python3 moneo.py -d workers -g -c ~/hostfile```
  Note: if install step has already been performed you can use the -w flag to skip it.
3. Verify that the exporters and publisher are running with ```ps -eaf | grep python3```
    ![image](https://user-images.githubusercontent.com/70273488/227356884-df1fbc1d-40d1-445c-95c8-756c93df5c10.png)
4. At this point the exporters and publisher shoud be working.
5. Check with Geneva dashboards to verify that the metrics are being ingested.
