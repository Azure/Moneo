#!/bin/bash

set -e

# install dependencies
source ./$(dirname "${BASH_SOURCE[0]}")/common.sh
command -v pip2 >/dev/null 2>&1 || python2 <(curl -s https://bootstrap.pypa.io/pip/2.7/get-pip.py)
pip2 install prometheus_client

# install DCGM
dcgm_check=`sudo dpkg-query -l`
if [[ $dcgm_check =~ "datacenter-gpu-manager" ]]; then
	echo "Dcgm already installed"
else
	echo "Installing Dcgm"
	DCGM_VERSION=2.4.4
	DCGM_GPUMNGR_URL=https://azhpcstor.blob.core.windows.net/azhpc-images-store/datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb
	wget --retry-connrefused --tries=3 --waitretry=5 $DCGM_GPUMNGR_URL
	FILE_NAME=$(basename $DCGM_GPUMNGR_URL)
	RLINK=$(readlink -f $FILE_NAME)
	Check="69ba98bbc4f657f6a15a2922aee0ea6b495fad49147d056a8f442c531b885e0e"
	checksum=`sha256sum $RLINK | awk '{print $1}'`
	if [[ $checksum != $Check ]]
	then
		echo "*** Error - Checksum verification failed"
        	echo "*** Error - Checksum verification failed" > dcgm_fail.log
		exit -1
	fi

	dpkg -i datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb && \
	rm -f datacenter-gpu-manager_${DCGM_VERSION}_amd64.deb
fi
exit 0
