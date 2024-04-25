#!/bin/bash
set -e

# Ethernet device naming, if not present it will use default eth0 name
ethernet_dev_name=$1

# Start NVIDIA, Net and Node Exporter
echo "Starting NVIDIA, Net and Node Exporter"

python3 exporters/nvidia_exporter.py  &

python3 exporters/net_exporter.py --inifiband_sysfs=/hostsys/class/infiniband &

if [ -n "$ethernet_dev_name" ]; then
    python3 exporters/node_exporter.py -e $ethernet_dev_name &
else
    python3 exporters/node_exporter.py &
fi

wait -n
exit $?
