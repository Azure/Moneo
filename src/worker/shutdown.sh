#!/bin/bash

arch="nvidia"

if [ -e '/dev/nvidiactl' ]; then
    arch="nvidia"
elif [ -e '/dev/kfd' ];then
    arch="amd"
else
	arch='cpu'
fi

kill_exporters() {
    pkill -f "${1}_exporter.py*"
	pkill -f "net_exporter.py*"
	pkill -f "node_exporter.py*"
}

if [ $arch == "nvidia" ]; then
	kill_exporters $arch
	pkill -f "metrics_publisher.py*"
	pkill -f "^nv-hostengine"
	sleep 3
	exit 0
elif [ $arch == "amd" ]; then
        kill_exporters $arch
	pkill -f "metrics_publisher.py*"
	pkill -f "^/opt/rocm/rdc/bin/rdcd"
	sleep 3
        exit 0
else
	echo "No GPU architecture detected"
fi
	exit 0
