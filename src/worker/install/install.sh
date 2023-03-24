#!/bin/bash
arch="nvidia"

PUBLISHER_INSTALL=$1

if [ -n "$PUBLISHER_INSTALL" ];
then
    if [ $PUBLISHER_INSTALL = true ];
    then
        $(dirname "${BASH_SOURCE[0]}")/geneva.sh  $(dirname "${BASH_SOURCE[0]}")/config/geneva_config.json
    fi
fi

if [ -e '/dev/nvidiactl' ]; then
# Nvidia
    $(dirname "${BASH_SOURCE[0]}")/nvidia.sh
elif [ -e '/dev/kfd' ];then
# AMD
    $(dirname "${BASH_SOURCE[0]}")/amd.sh
else
	source $(dirname "${BASH_SOURCE[0]}")/common.sh
fi
