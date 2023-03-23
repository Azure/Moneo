#!/bin/bash

set -e

# install dependencies
command -v pip3 >/dev/null 2>&1 || python3 <(curl -s https://bootstrap.pypa.io/get-pip.py)
python3 -m pip install prometheus_client psutil filelock opentelemetry-sdk opentelemetry-exporter-otlp
