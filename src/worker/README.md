Install
=======

NVIDIA Node
-----------

```sh
sudo bash install/nvidia.sh

# start DCGM daemon
sudo nv-hostengine &
# start DCGM exporter (DCGM only supports Python2 currently)
python2 exporters/nvidia_exporter.py &
# start net exporter
python3 exporters/net_exporter.py &
```

AMD Node
--------

```sh
sudo bash install/amd.sh

# start RDC daemon
sudo /opt/rocm/rdc/bin/rdcd -u &
# start RDC exporter
python3 exporters/rdc_exporter.py &
# start net exporter
python3 exporters/net_exporter.py &
```
