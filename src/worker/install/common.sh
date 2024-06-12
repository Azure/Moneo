#!/bin/bash

set -e

# install dependencies
# install DCGM
distro=`awk -F= '/^NAME/{print $2}' /etc/os-release`
if [[ $distro =~ "Ubuntu" ]]; then
    apt-get install -y python3-dev
elif [[ $distro =~ (AlmaLinux|Rocky Linux) ]]; then
    yum install -y python3-devel
else
	echo "OS version is not supported"
fi

command -v pip3 >/dev/null 2>&1 || python3 <(curl -s https://bootstrap.pypa.io/get-pip.py)
python3 -m pip -qqq install prometheus_client psutil filelock
