FROM nvidia/cuda:11.1.1-runtime-ubuntu18.04

LABEL maintainer="Moneo"

ARG BRANCH_OR_TAG=main
ENV PROFILING false

# Install dependencies
RUN apt-get update -y       \
    && apt-get install -y   \
    --no-install-recommends \
    git                     \
    curl                    \
    sudo                    \
    wget                    \
    libgomp1                \
    python3.8               \
    python3-pip

# Link python3 to python3.8
RUN cd /usr/bin/            \
    && rm python3           \
    && ln -s /usr/bin/python3.8 python3

RUN python3 -m pip install --upgrade pip

# Clone Moneo repository
RUN git config --global advice.detachedHead false
RUN git clone --branch ${BRANCH_OR_TAG} https://github.com/Azure/Moneo.git

# Install DCGM
WORKDIR Moneo/src/worker
RUN sudo bash install/nvidia.sh

# Set EntryPoint
COPY moneo-exporter-nvidia_entrypoint.sh .
RUN chmod +x moneo-exporter-nvidia_entrypoint.sh
CMD /bin/bash moneo-exporter-nvidia_entrypoint.sh ${PROFILING}
