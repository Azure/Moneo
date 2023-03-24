#!/bin/bash

set -e

# install dependencies
# install DCGM
if [[ $distro =~ "Ubuntu" ]]; then
    apt-get install -y python3-dev
elif [[ $distro =~ "AlmaLinux" ]]; then
    yum install -y python3-dev
else
	echo "OS version is not supported"
fi

command -v pip3 >/dev/null 2>&1 || python3 <(curl -s https://bootstrap.pypa.io/get-pip.py)
python3 -m pip install prometheus_client psutil filelock opentelemetry-sdk opentelemetry-exporter-otlp
