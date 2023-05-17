#!/bin/bash

arch="nvidia"

remove_docker=$1

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
    pkill -f "metrics_publisher.py*"
}

kill_docker() {
    if [[ $(docker ps -a | grep genevamdmagent) ]]; then
        echo "Stopping Geneva Metrics Extension(MA) Container"
        docker stop genevamdmagent
        docker rm genevamdmagent
    fi
    if [[ $(docker ps -a | grep prometheus) ]]; then
        echo "Stopping Prometheus Container"
        docker stop prometheus
        docker rm prometheus
    fi
    if [[ $(docker ps -a | grep prometheus_sidecar) ]]; then
        echo "Stopping prometheus Sidecar Container"
        docker stop prometheus_sidecar
        docker rm prometheus_sidecar
    fi
}

if [ $arch == "nvidia" ]; then
    kill_exporters $arch
    pkill -f "^nv-hostengine"

	if [ $remove_docker == "true" ]; then
		kill_docker
	else
		echo "Not removing docker containers"
	fi

    sleep 3
    exit 0
elif [ $arch == "amd" ]; then
    kill_exporters $arch
    pkill -f "^/opt/rocm/rdc/bin/rdcd"
    sleep 3
        exit 0
else
    kill_exporters
    kill_docker
    echo "No GPU architecture detected"
fi
    exit 0
