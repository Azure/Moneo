#!/bin/bash/

arch=$1

if [ $arch == "nvidia" ]; then
	pkill -f "nvidia_exporter.py*" && sleep 1
	pkill -f "net_exporter.py*" && sleep 1
	pkill -f "^nv-hostengine"
	sleep 3
	echo 0 >&2
elif [ $arch == "amd" ]; then
	pkill -f "amd_exporter.py*" && sleep 1
	pkill -f "net_exporter.py*" && sleep 1
	pkill -f "^/opt/rocm/rdc/bin/rdcd"
	sleep 3
	echo 0 >&2
else
	echo "Proper architecture not provided. Choices are nvidia and amd."
fi
