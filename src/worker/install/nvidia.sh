#!/bin/bash

set -e

# install dependencies
source $(dirname "${BASH_SOURCE[0]}")/common.sh


distro=`awk -F= '/^NAME/{print $2}' /etc/os-release`
echo $distro

ubuntu_dcgm_install () {
  		echo "Installing Dcgm"
		apt-get update \
    		&& sudo apt-get install -y datacenter-gpu-manager
}

alma_dcgm_install () {
		echo "Installing Dcgm"
		yum-config-manager --add-repo=https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/cuda-rhel8.repo
		sudo yum install dcgm
}

check_min_dcgm_ver(){
	DCGM_VER=`dcgmi --version |grep version | awk -F ': ' '{print $2}'`
	REQ_VER="3.1.6"
	if [ "$(printf '%s\n' "$REQ_VER" "$DCGM_VER" | sort -V | head -n1)" = "$REQ_VER" ]; then 
			echo "A suitable version of Dcgm is already installed"
	else
			echo "removing old DCGM"
			# remove old version
			if [[ $distro =~ "Ubuntu" ]]; then
				apt -y remove datacenter-gpu-manager
			elif [[ $distro =~ "AlmaLinux" ]]; then
				yum -y remove datacenter-gpu-manager
			fi
			$1
	fi

}


# install DCGM
if [[ $distro =~ "Ubuntu" ]]; then
	dcgm_check=`sudo dpkg-query -l`
	if [[ $dcgm_check =~ "datacenter-gpu-manager" ]]; then
		check_min_dcgm_ver ubuntu_dcgm_install

	else
		ubuntu_dcgm_install
	fi
elif [[ $distro =~ "AlmaLinux" ]]; then
	dcgm_check=`rpm -qa`
	if [[ $dcgm_check =~ "datacenter-gpu-manager" ]]; then
		check_min_dcgm_ver alma_dcgm_install
	else
		alma_dcgm_install
	fi
else
	echo "OS version is not supported"
fi

exit 0
