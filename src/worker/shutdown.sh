#!/bin/bash/

arch=$1

kill_exporters() {
    pkill -f "${1}_exporter.py*" && sleep 1
	pkill -f "net_exporter.py*" && sleep 1
	pkill -f "node_exporter.py*" && sleep 1
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
