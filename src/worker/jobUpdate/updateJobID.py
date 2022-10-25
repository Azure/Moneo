import os
import sys
import json
import logging

path = os.path.dirname(__file__)
if path:
    path = path + '/'
p = os.path.abspath(path + '../helpers')
sys.path.insert(1, p)
from shmem_helper import Shared_Mem_Mngr
from lock_helper import file_lock_mgr

JobShm = {
    "jobid": [],
    "GPU": {},
    "HCA": {}
}

logging.basicConfig(level=logging.DEBUG)

job_config = {
    # to synchronixe job multiple job updates
    "HCA": {"lock": file_lock_mgr("/tmp/JobIbMoneo.txt.lock")},
    # to synchronixe job multiple job updates
    "GPU": {"lock": file_lock_mgr("/tmp/JobNvMoneo.txt.lock")}
}


class JobUpdateMgr:

    def __init__(self, config):
        self.job_config = config
        self.job_config["HCA"]["shm_mgr"] = Shared_Mem_Mngr(
            "ib_moneo_SM", isClient=True)  # for IB exporter
        self.job_config["GPU"]["shm_mgr"] = Shared_Mem_Mngr(
            "nv_moneo_SM", isClient=True)  # for nv exporter

    def getCurrentJobConfig(self, device):
        shm = self.job_config[device]["shm_mgr"].get_shm()
        size = shm._size
        msg = bytes(shm.buf[:size]).decode('utf-8')
        config = json.loads(msg)
        return config, size

    def updateShm(self, data, device):
        self.job_config[device]["lock"].acquire()
        try:
            config, currentSize = self.getCurrentJobConfig(device)
            print(data)
            for dev_name in data[device]:
                # device name is not being requested/it is
                # not in the users config to be updated
                if dev_name not in config[device].keys():
                    logging.debug("key mismatch on  %s devices %s",
                                  device, dev_name)
                    continue
                # Update device name to user specified ID
                if config[device][dev_name] is None:
                    config[device][dev_name] = data[device][dev_name]
                    config["Updated"] = 1
                    logging.debug("update job id on  %s devices, data %s ",
                                  device, data[device][dev_name])
                # User requested update but device has another ID on it. Must
                # be set to none before an update.
                elif data[device][dev_name] is None:
                    config[device][dev_name] = None
                    config["Updated"] = 1
                    logging.debug("Resetting job id on  %s devices", device)
                # raise exception if ID for device is not None.
                # We do not want to overwrite another job
                else:
                    logging.debug("Exception raised", device)
                    raise Exception(
                        "Failed to update job. Devices are set to a job Id. \
                        Need to be set to None first before new upodate.")
            msg = json.dumps(config)
            # check new size vs old size
            msgSize = len(msg.encode("utf8"))
            if msgSize != currentSize:
                logging.debug("Resizing shared memory for %s devices", device)
                self.job_config[device]["shm_mgr"].resize_shm(data=msg)
            else:
                logging.debug("Not resizing shmem for %s devices", device)
                shm = self.job_config[device]["shm_mgr"].get_shm()
                shm.buf[:msgSize] = bytes(msg, 'UTF-8')
        finally:
            self.job_config[device]["lock"].release()


def makeDummyDataHCA(id=None):
    for hca in range(8):
        JobShm["HCA"]["mlx5_ib" + str(hca)] = id


def makeDummyDataGPU(id=None):
    for gpu in range(8):
        JobShm["GPU"][str(gpu)] = id


def test_GPU():  # must have nvidia exporter running
    jmgr = JobUpdateMgr(job_config)
    makeDummyDataGPU("dummyid")
    jmgr.updateShm(JobShm, device="GPU")
    shm1, size = jmgr.getCurrentJobConfig("GPU")
    makeDummyDataGPU()
    jmgr.updateShm(JobShm, device="GPU")
    shm2, size = jmgr.getCurrentJobConfig("GPU")
    logging.info("Shmem contents first pass: %s\nSecond pass: %s ", shm1, shm2)


def test_IB():  # must have IB exporter running
    jmgr = JobUpdateMgr(job_config)
    makeDummyDataHCA("dummyid")
    jmgr.updateShm(JobShm, device="HCA")
    shm1, size = jmgr.getCurrentJobConfig("HCA")
    makeDummyDataHCA()
    jmgr.updateShm(JobShm, device="HCA")
    shm2, size = jmgr.getCurrentJobConfig("HCA")
    logging.info("Shmem contents first pass: %s", shm1)


if __name__ == '__main__':
    # test_GPU()
    test_IB()
    print("done")
