#!/bin/bash

arch="nvidia"

if [ -e '/dev/nvidiactl' ]; then
# Nvidia
    $(dirname "${BASH_SOURCE[0]}")/nvidia.sh
elif [ -e '/dev/kfd' ];then
# AMD
    $(dirname "${BASH_SOURCE[0]}")/amd.sh
else
	source $(dirname "${BASH_SOURCE[0]}")/common.sh
fi
