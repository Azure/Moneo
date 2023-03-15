#!/bin/bash

#start exporters
if [ -e "/dev/nvidiactl" ];
then
    nohup python3 exporters/nvidia_exporter.py  </dev/null >/dev/null 2>&1 &
fi
if [ -d "/sys/class/infiniband" ];
then
    nohup python3 exporters/net_exporter.py </dev/null >/dev/null 2>&1 &
fi

nohup python3 exporters/node_exporter.py </dev/null >/dev/null 2>&1 &