#!/bin/bash

set -e

# install dependencies
source ./$(dirname "${BASH_SOURCE[0]}")/common.sh

# install DCGM
distro=`awk -F= '/^NAME/{print $2}' /etc/os-release`
echo $distro


if [[ $distro =~ "Ubuntu" ]]; then
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
elif [[ $distro =~ "AlmaLinux" ]]; then
	dcgm_check=`yum list --installed `
	if [[ $dcgm_check =~ "datacenter-gpu-manager" ]]; then
		echo "Dcgm already installed"
	else
		echo "Installing Dcgm"
		DCGM_VERSION=2.4.4
		DCGM_URL=https://azhpcstor.blob.core.windows.net/azhpc-images-store/datacenter-gpu-manager-${DCGM_VERSION}-1-x86_64.rpm
		wget --retry-connrefused --tries=3 --waitretry=5 $DCGM_URL
		FILE_NAME=$(basename $DCGM_URL)
		RLINK=$(readlink -f $FILE_NAME)
		Check="1d8fbe97797fada8048a7832bfac4bc7d3ad661bb24163d21324965ae7e7817d"
		checksum=`sha256sum $RLINK | awk '{print $1}'`
		if [[ $checksum != $Check ]]
		then
			echo "*** Error - Checksum verification failed"
			echo "*** Error - Checksum verification failed" > dcgm_fail.log
			exit -1
		fi
		rpm -i datacenter-gpu-manager-${DCGM_VERSION}-1-x86_64.rpm
		rm -f datacenter-gpu-manager-${DCGM_VERSION}-1-x86_64.rpm
	fi
else
	echo "OS version is not supported"
fi

exit 0
