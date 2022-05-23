#!/bin/bash

# install dependencies
source ./$(dirname "${BASH_SOURCE[0]}")/common.sh
apt-get install -y automake make g++ unzip build-essential autoconf libtool pkg-config libgflags-dev libgtest-dev clang-5.0 libc++-dev curl libcap-dev

# install grpc
export GRPC_LIB_DIR=/usr/local/lib
git clone -b v1.28.1 https://github.com/grpc/grpc ~/grpc
cd ~/grpc
git submodule update --init
mkdir -p cmake/build
cd cmake/build
cmake -DgRPC_INSTALL=ON -DBUILD_SHARED_LIBS=ON ../..
make -j
make install
echo ${GRPC_LIB_DIR} | tee /etc/ld.so.conf.d/grpc.conf

# install RDC
export RDC_LIB_DIR=/opt/rocm/rdc/lib
git clone https://github.com/RadeonOpenCompute/rdc ~/rdc
mkdir -p ~/rdc/build
cd ~/rdc/build
cmake -DROCM_DIR=/opt/rocm -DGRPC_ROOT="/usr/local" ..
make -j
make install
cat > /etc/ld.so.conf.d/x86_64-librdc_client.conf <<EOF
${GRPC_LIB_DIR}
${GRPC_LIB_DIR}64
${RDC_LIB_DIR}
${RDC_LIB_DIR}64
EOF
ldconfig
