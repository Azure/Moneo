Moneo Exporter
=====
Description
-----
If you want to run Moneo in k8s cluster environment, moneo supports a way to only run moneo-worker inside the container to export metrics. In this doc, you can know how to build images and deploy moneo-exporter manually.

Steps
-----
### Build image
We need to build a moneo-exporter docker image firstly.
1. checkout the code from github.
```bash
rm -rf ./Moneo
git init Moneo
cd Moneo
git remote add origin https://github.com/Azure/Moneo.git
git fetch origin
```
You will see following result:
```bash
root@azureuser:~$ rm -rf ./Moneo
git init Moneo
cd Moneo
git remote add origin https://github.com/Azure/Moneo.git
git fetch origin
Initialized empty Git repository in /root/Moneo/.git/
remote: Enumerating objects: 522, done.
remote: Counting objects: 100% (305/305), done.
remote: Compressing objects: 100% (236/236), done.
remote: Total 522 (delta 183), reused 107 (delta 64), pack-reused 217
Receiving objects: 100% (522/522), 181.80 KiB | 483.00 KiB/s, done.
Resolving deltas: 100% (233/233), done.
From https://github.com/Azure/Moneo
 * [new branch]      main       -> origin/main
 * [new tag]         v0.1.0     -> v0.1.0
 * [new tag]         v0.1.1     -> v0.1.1
 * [new tag]         v0.1.2     -> v0.1.2
 * [new tag]         v0.2.0     -> v0.2.0
 * [new tag]         v0.2.1     -> v0.2.1
 * [new tag]         v0.2.2     -> v0.2.2
```
2. Build the Moneo-exporter image. Currently, Moneo-exporter only supports nvidia platform.
```bash
cd dockerfile
sudo docker build 
    --build-arg BRANCH_OR_TAG=<specific branch or tag>
    -t moneo-exporter-nvidia:latest
    -f moneo-exporter-nvidia.dockerfile .
```
### Run Container
After building the docker image, we need to run container and start the moneo-exporter.
1. Run container
```bash
docker run 
    --name=moneo-exporter-nvidia
    --rm --runtime=nvidia
    --net=host
    -e PROFILING=<true/false>
    -e GPU_SAMPLE_RATE=<gpu_sample_rate:(1,2,10)>
    --cap-add SYS_ADMIN 
    -v /sys:/hostsys
    -itd moneo-exporter-nvidia:latest
```
2. Check the port 8000, 8001, 8002 is up, which is the moneo-exporter listening to:
```bash
root@azureuser:~$ sudo netstat -tulpn | grep LISTEN | grep python3
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      94787/python3       
tcp        0      0 0.0.0.0:8001            0.0.0.0:*               LISTEN      94788/python3  
tcp        0      0 0.0.0.0:8002            0.0.0.0:*               LISTEN      94789/python3  
```
3. Get the prometheus metrics from Moneo-exporter.
```bash
curl localhost:8000
curl localhost:8001
curl localhost:8002
```
You can see the following prometheus metrics just as below, which means moneo-exporter can work normally.
```bash
root@azureuser:~$ curl localhost:8000
...
# HELP dcgm_sm_clock SM clock frequency (in MHz)
# TYPE dcgm_sm_clock gauge
dcgm_sm_clock{gpu_id="0",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="1",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="2",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="3",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="4",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="5",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="6",gpu_uuid="********",job_id="None"} 210.0
dcgm_sm_clock{gpu_id="7",gpu_uuid="********",job_id="None"} 210.0
...
root@azureuser:~$ curl localhost:8001
...
# HELP ib_port_xmit_data ib_port_xmit_data
# TYPE ib_port_xmit_data gauge
ib_port_xmit_data{ib_port="mlx5_ib2:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib0:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib7:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib5:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib3:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib1:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib6:1",ib_sys_guid="********",job_id="None"} 0.0
ib_port_xmit_data{ib_port="mlx5_ib4:1",ib_sys_guid="********",job_id="None"} 0.0
...
root@azureuser:~$ curl localhost:8001
...
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 104.0
python_gc_objects_collected_total{generation="1"} 304.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP node_mem_available node_mem_available
# TYPE node_mem_available gauge
node_mem_available{job_id="None"} 1.841545956e+09
# HELP node_mem_util node_mem_util
# TYPE node_mem_util gauge
node_mem_util{job_id="None"} 0.9
# HELP node_xid_error node_xid_error
# TYPE node_xid_error gauge
# HELP node_link_flap node_link_flap
# TYPE node_link_flap gauge
...
```