#!/bin/bash
set -e

# Stops previous instances of AMD RDC Daemon and Exporter
bash shutdown.sh

# Launches AMD RDC Daemon
nohup /opt/rocm/bin/rdcd -u </dev/null >/dev/null 2>&1 &

# Initiates AMD and Network Exporters
echo "Starting AMD and Network Exporters"

# Starts AMD Exporter
python3 exporters/amd_exporter.py &
echo "AMD Exporter Started!"

# Starts Network Exporter with specified InfiniBand sysfs path
python3 exporters/net_exporter.py --inifiband_sysfs=/hostsys/class/infiniband &
echo "Network Exporter Started!"

# Starts Node Exporter
python3 exporters/node_exporter.py &
echo "Node Exporter Started!"

# Waits for any process to exit and returns the exit status
wait -n
exit $?
