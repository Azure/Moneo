# Use ROCm development image
FROM rocm/dev-ubuntu-22.04:6.1.1

# Metadata
LABEL maintainer="Moneo"

# Environment variables
ENV ROCM_VERSION=6.1.1 \
    DEBIAN_FRONTEND=noninteractive

# Work directory setup
WORKDIR /root/Moneo
COPY . .

# Installing packages and setting up Python
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    numactl git curl cmake ibverbs-utils sudo systemd wget libgomp1 libcap2-bin python3.10 python3-pip && \
    cd /usr/bin && rm python3 && ln -s python3.10 python3 && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install prometheus_client psutil

# # RDC installation
WORKDIR /root/Moneo/src/worker
RUN sudo bash install/amd.sh

# Set EntryPoint
COPY dockerfile/moneo-exporter-amd_entrypoint.sh .
RUN chmod +x moneo-exporter-amd_entrypoint.sh

# Final CMD
CMD ["/bin/bash", "moneo-exporter-amd_entrypoint.sh"]
