#!/bin/bash

set -e

# install dependencies
source ./$(dirname "${BASH_SOURCE[0]}")/common.sh
apt-get install -y automake make g++ unzip build-essential autoconf libtool pkg-config libgflags-dev libgtest-dev libc++-dev curl libcap-dev

# install grpc
export GRPC_ROOT=/opt/grpc

# Check if the directory exists and is not empty
if [ -d "$GRPC_ROOT" ] && [ "$(ls -A $GRPC_ROOT)" ]; then
    cd "$GRPC_ROOT"
    git pull
else
    git clone -b v1.59.1 https://github.com/grpc/grpc --depth=1 --shallow-submodules --recurse-submodules "$GRPC_ROOT"
    cd "$GRPC_ROOT"
fi
cmake -B build \
    -DgRPC_INSTALL=ON \
    -DgRPC_BUILD_TESTS=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX="$GRPC_ROOT" \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_BUILD_TYPE=Release
make -C build -j $(nproc)
make -C build install
echo "$GRPC_ROOT" | sudo tee /etc/ld.so.conf.d/grpc.conf


# install rdc
export RDC_ROOT=/opt/rdc
# Check if the directory exists and is not empty
if [ -d "$RDC_ROOT" ] && [ "$(ls -A $RDC_ROOT)" ]; then
    cd "$RDC_ROOT"
    git pull
else
    git clone https://github.com/RadeonOpenCompute/rdc "$RDC_ROOT"
    cd "$RDC_ROOT"
fi
# default installation location is /opt/rocm, specify with -DROCM_DIR or -DCMAKE_INSTALL_PREFIX
cmake -B build -DGRPC_ROOT="$GRPC_ROOT" -DROCM_DIR="/opt/rocm" -DCMAKE_INSTALL_PREFIX="/opt/rocm"
make -C build -j $(nproc)
make -C build install

# Update ldconfig
export RDC_LIB_DIR=/opt/rocm/lib/rdc
export GRPC_LIB_DIR=/opt/grpc/lib
echo -e "${GRPC_LIB_DIR}\n${GRPC_LIB_DIR}64" | sudo tee /etc/ld.so.conf.d/x86_64-librdc_client.conf
echo -e "${RDC_LIB_DIR}\n${RDC_LIB_DIR}64" | sudo tee -a /etc/ld.so.conf.d/x86_64-librdc_client.conf
ldconfig
