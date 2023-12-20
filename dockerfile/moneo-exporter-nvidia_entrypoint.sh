#!/bin/bash
set -e

enable_profiling=$1
gpu_sample_rate=$2
# Start NVIDIA DCGM Daemon
# echo "Starting NVIDIA DCGM Daemon"
# nv-hostengine

# Start NVIDIA, Net and Node Exporter
echo "Starting NVIDIA, Net and Node Exporter"

if [ $enable_profiling = true ]; then
    python3 exporters/nvidia_exporter.py -m -s $gpu_sample_rate &
else
    python3 exporters/nvidia_exporter.py -s $gpu_sample_rate &
fi

python3 exporters/net_exporter.py --inifiband_sysfs=/hostsys/class/infiniband &
python3 exporters/node_exporter.py &

wait -n
exit $?
