#!/bin/bash

# Usage ./managerLaunch <hostfile> <manager hostname/ip>

WORK_DIR=/tmp/moneo-master
GRAF_CONFIG=$WORK_DIR/grafana/provisioning/datasources/prometheus.yml
PROM_CONFIG=$WORK_DIR/prometheus.yml
JOB_NAMES=("dcgm_exporter" "net_exporter" "node_exporter")
HOSTS=`cat $1`
MANAGER=$2

# generate config file for Prometheus exporters
generate_prom(){
    HOSTLIST=''
    HOSTLIST1=''
    HOSTLIST2=''
    WORKER_LIST="$@"
    for i in $WORKER_LIST
    do
        if [ "${i}" = "" ];
            then
                continue
        fi 
        HOSTLIST+="        - ${i}:8000\n"
        HOSTLIST1+="        - ${i}:8001\n"
        HOSTLIST2+="        - ${i}:8002\n"
    done
    #delete extra place holder
    sed -i '/moneo-worker-1/d' $PROM_CONFIG
    #replace other place holder with host:port list
    sed -i -r "s/\s+- moneo-worker-0:8000/$HOSTLIST/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8001/$HOSTLIST1/" $PROM_CONFIG
    sed -i -r "s/\s+- moneo-worker-0:8002/$HOSTLIST2/" $PROM_CONFIG
}

# generate config file for grafana data source
generate_graf(){
    sed -i -r "s/moneo-master/$1/" $GRAF_CONFIG
}

#modify template for usage
generate_prom $HOSTS
generate_graf $MANAGER

pushd $WORK_DIR
#stop running instances
docker rm -f prometheus || true
docker rm -f grafana || true

sudo bash run.sh
popd

