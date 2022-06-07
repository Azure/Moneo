#!/bin/bash

# start prometheus
mkdir -m 777 /mnt/prometheus
docker rm -f prometheus || true
docker run --name prometheus \
    -it --net=host -d -p 9090:9090 \
    -v /mnt/prometheus:/prometheus \
    -v $PWD/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus \
    --storage.tsdb.path=/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.enable-admin-api
# reload config
# docker exec -it prometheus killall -HUP prometheus

# start grafana
docker rm -f grafana || true
docker run --name grafana \
    -it --net=host  -d -p 3000:3000 \
    --env-file $PWD/grafana/grafana.env \
    -v $PWD/grafana/dashboards:/var/lib/grafana/dashboards \
    -v $PWD/grafana/provisioning:/etc/grafana/provisioning \
    grafana/grafana
