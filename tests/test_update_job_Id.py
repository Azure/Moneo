import unittest
import os
import sys
from filelock import FileLock
import json
p = os.path.abspath('../src/worker')
sys.path.insert(1, p)
from helpers.shmem_helper import clean_Leaked_shm
from helpers.shmem_helper import Shared_Mem_Mngr
from jobUpdate.updateJobID import JobUpdateMgr

"""Moneo JobUpdate test module"""

JobShm = {
    "jobid": [],
    "GPU": {},
    "HCA": {}
}

job_config = {
    # to synchronixe job multiple job updates
    "HCA": {"lock": FileLock("/tmp/test_JobIbMoneo.txt.lock", timeout=5)},
    # to synchronixe job multiple job updates
    "GPU": {"lock": FileLock("/tmp/test_JobNvMoneo.txt.lock", timeout=5)}
}


def cleanUp(shm_name):
    """clean up rogue shared memory"""
    try:
        # in the event of a previous unclean exit. Clean up leaked resouces
        clean_Leaked_shm(shm_name)
    except FileNotFoundError:
        pass


class JobUpdateTestCase(unittest.TestCase):
    """Job Update test Class."""

    def test_jobUpdate_shmem(self):  # must have nvidia exporter running
        cleanUp("nv_moneo_SM")
        serverMgr = Shared_Mem_Mngr("nv_moneo_SM", isClient=False)
        initialShm = {
            "GPU": {0: None, 1: None, 2: None,
                    3: None, 4: None, 5: None, 6: None, 7: None}
        }
        data = json.dumps(initialShm)  # serialize
        serverMgr.create_shm(data)
        try:
            jmgr = JobUpdateMgr(job_config)
            self.makeDummyDataGPU("dummyid")
            jmgr.updateShm(JobShm, device="GPU")
            shm1, size = jmgr.getCurrentJobConfig("GPU")
            # check None -> id update path
            assert (shm1["GPU"]['0'] == "dummyid")
            self.makeDummyDataGPU("newid")
            fail = False
            try:
                jmgr.updateShm(JobShm, device="GPU")
            except Exception:
                fail = True
            # check current job id -> new id, Should not overwrite.
            # Exception expected
            assert (fail)
            self.makeDummyDataGPU()
            jmgr.updateShm(JobShm, device="GPU")
            shm2, size = jmgr.getCurrentJobConfig("GPU")
            assert (not shm2["GPU"]['0'])  # check jobID -> None path

        finally:
            serverMgr.delete_shm()

    def makeDummyDataGPU(self, id=None):
        global JobShm
        for gpu in range(8):
            JobShm["GPU"][str(gpu)] = id


if __name__ == '__main__':
    unittest.main()
