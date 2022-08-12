#!/bin/bash

set -e

# install dependencies
source ./$(dirname "${BASH_SOURCE[0]}")/common.sh
command -v pip2 >/dev/null 2>&1 || python2 <(curl -s https://bootstrap.pypa.io/pip/2.7/get-pip.py)
pip2 install prometheus_client

# install DCGM
dcgm_check=`sudo dpkg-query -l | grep datacenter-gpu-manager`
if [[ $dcgm_check =~ "datacenter-gpu-manager" ]]; then
	echo "Dcgm installed"
else
	echo "installing Dcgm"
	DCGM_VERSION=2.4.4
	DCGM_GPUMNGR_URL=https://azhpcstor.blob.core.windows.net/azhpc-images-store/datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb
	dpkg -i datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb && \
	rm -f datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb
	# Create service for dcgm to launch on bootup
	bash -c "cat > /etc/systemd/system/dcgm.service" <<'EOF'
	[Unit]
	Description=DCGM service
	[Service]
	User=root
	PrivateTmp=false
	ExecStart=/usr/bin/nv-hostengine -n
	Restart=on-abort
	[Install]
	WantedBy=multi-user.target
EOF

	systemctl enable dcgm
	systemctl start dcgm
fi	
#distribution=$(. /etc/os-release; echo $ID$VERSION_ID | sed -e 's/\.//g')
#architecture=x86_64
#echo "deb http://developer.download.nvidia.com/compute/cuda/repos/$distribution/$architecture /" | tee /etc/apt/sources.list.d/cuda.list
#apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/$distribution/$architecture/7fa2af80.pub
#wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/$architecture/cuda-$distribution.pin -O /etc/apt/preferences.d/cuda-repository-pin-600
#apt-get update
#apt-get install -y datacenter-gpu-manager
