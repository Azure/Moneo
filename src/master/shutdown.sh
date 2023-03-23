#!/bin/bash

docker rm -f prometheus || true
docker rm -f grafana || true
pkill -f "azinsights_main.py*" || true
