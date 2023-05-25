#!/bin/bash
#run this from a head node. A compute node can also double as head node

MONEO_DIR=$1
HOSTFILE=$2

PSSH_ARGS="-x '-o StrictHostKeyChecking=no' -i -t 0 -h $HOSTFILE"

distro=`awk -F= '/^NAME/{print $2}' /etc/os-release`
if [[ $distro =~ "Ubuntu" ]]; then
    PSSH="parallel-ssh"
elif [[ $distro =~ "AlmaLinux" ]]; then
    PSSH="pssh"
else
	echo "OS version is not supported"
    exit 1
fi

PSSH="$PSSH $PSSH_ARGS \"sudo $MONEO_DIR/linux_services/configure.sh $MONEO_DIR\""
echo $PSSH 
$PSSH 
#$PSSH "sudo $MONEO_DIR/linux_services/configure.sh $MONEO_DIR" 



