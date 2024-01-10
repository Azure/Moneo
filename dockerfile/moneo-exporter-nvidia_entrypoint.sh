#!/bin/bash
set -e

enable_profiling=$1
gpu_sample_rate=$2
ethernet_dev_name=$3

# Start NVIDIA, Net and Node Exporter
echo "Starting NVIDIA, Net and Node Exporter"

if [ $enable_profiling = true ]; then
    python3 exporters/nvidia_exporter.py -m -s $gpu_sample_rate &
else
    python3 exporters/nvidia_exporter.py -s $gpu_sample_rate &
fi

python3 exporters/net_exporter.py --inifiband_sysfs=/hostsys/class/infiniband &

if [-n $ethernet_dev_name]; then
    python3 exporters/node_exporter.py -e $ethernet_dev_name &
else
    python3 exporters/node_exporter.py &
fi

wait -n
exit $?
