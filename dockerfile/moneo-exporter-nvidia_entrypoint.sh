#!/bin/bash
set -e

enable_profiling=$1
# Start NVIDIA DCGM Daemon
echo "Starting NVIDIA DCGM Daemon"
nv-hostengine

# Start NVIDIA and Net Exporter
echo "Starting NVIDIA and Net Exporter"

if [ $enable_profiling = true ]; then
    python3 exporters/nvidia_exporter.py -m &
else
    python3 exporters/nvidia_exporter.py &
fi

python3 exporters/net_exporter.py --inifiband_sysfs=/hostsys/class/infiniband &

wait -n
exit $?
