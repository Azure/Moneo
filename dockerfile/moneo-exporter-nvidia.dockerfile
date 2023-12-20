FROM nvcr.io/nvidia/cuda:12.2.2-runtime-ubuntu22.04

LABEL maintainer="Moneo"

ARG BRANCH_OR_TAG=main
ARG DCGM_VERSION=3.1.1
ENV PROFILING false
ENV GPU_SAMPLE_RATE 2

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update -y                           \
    && apt-get install -y                       \
    --no-install-recommends                     \
    numactl                                     \
    git                                         \
    curl                                        \
    sudo                                        \
    systemd                                     \
    wget                                        \
    libgomp1                                    \
    libcap2-bin                                 \
    datacenter-gpu-manager                      \
    python3.10                                  \
    python3-pip

# Link python3 to python3.10
RUN cd /usr/bin/                                \
    && rm python3                               \
    && ln -s /usr/bin/python3.10 python3

RUN python3 -m pip install --upgrade pip

# Install OFED
ENV OFED_VERSION=23.07-0.5.1.2
RUN cd /tmp && \
    wget -q https://content.mellanox.com/ofed/MLNX_OFED-${OFED_VERSION}/MLNX_OFED_LINUX-${OFED_VERSION}-ubuntu22.04-x86_64.tgz && \
    tar xzf MLNX_OFED_LINUX-${OFED_VERSION}-ubuntu22.04-x86_64.tgz && \
    MLNX_OFED_LINUX-${OFED_VERSION}-ubuntu22.04-x86_64/mlnxofedinstall --user-space-only --without-fw-update --without-ucx-cuda --force --all && \
    rm -rf /tmp/MLNX_OFED_LINUX-${OFED_VERSION}*

# Clone Moneo repository
RUN git config --global advice.detachedHead false
RUN git clone --branch ${BRANCH_OR_TAG} https://github.com/Azure/Moneo.git

# Install DCGM
WORKDIR Moneo/src/worker
RUN sudo bash install/nvidia.sh

# Set EntryPoint
COPY dockerfile/moneo-exporter-nvidia_entrypoint.sh .
RUN chmod +x moneo-exporter-nvidia_entrypoint.sh
CMD /bin/bash moneo-exporter-nvidia_entrypoint.sh ${PROFILING} ${GPU_SAMPLE_RATE}

