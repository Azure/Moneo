#!/bin/bash/

arch=$1

kill_exporters() {
    pkill -f "${1}_exporter.py*"
	pkill -f "net_exporter.py*"
	pkill -f "node_exporter.py*"
}

if [ $arch == "nvidia" ]; then
	kill_exporters $arch
	pkill -f "^nv-hostengine"
	sleep 3
	exit 0
elif [ $arch == "amd" ]; then
        kill_exporters $arch
	pkill -f "^/opt/rocm/rdc/bin/rdcd"
	sleep 3
        exit 0
else
	echo "Proper architecture not provided. Choices are nvidia and amd."
fi
	exit 0
