#!/bin/bash

docker rm -f prometheus || true
docker rm -f grafana || true
docker rm -f prometheus_sidecar || true
pkill -f "azinsights_main.py*" || true
