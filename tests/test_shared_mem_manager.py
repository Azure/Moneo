import unittest
import os
import sys

p = os.path.abspath('../src/worker/helpers')
sys.path.insert(1, p)
from shmem_helper import clean_Leaked_shm
from shmem_helper import Shared_Mem_Mngr

"""Moneo Shared Memory test"""


class SharedMemTestCase(unittest.TestCase):
    """Shared Mem unit test Class."""

    def test_client_class(self):
        """test if client access read memory"""
        try:
            # in the event of a previous unclean exit. Clean up leaked resouces
            clean_Leaked_shm("psm_moneoSM")
        except FileNotFoundError:
            pass
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        clientMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=True)
        # try to access non-existent shared mem
        shm = clientMgr.get_shm()
        assert (shm is None)
        # creat memory and check client can access it
        data = "hello world"
        serverMgr.create_shm(data)  # create mem and assign it data
        shm = clientMgr.get_shm()
        assert ("psm_moneoSM" in shm._name)  # the stored name has a slash
        msg = bytes(shm.buf[:11]).decode('utf-8')  # bytes to string
        assert (msg == "hello world")
        serverMgr.delete_shm()

    def test_server_class(self):
        """test if server access read memory"""
        try:
            # in the event of a previous unclean exit. Clean up leaked resouces
            clean_Leaked_shm("psm_moneoSM")
        except FileNotFoundError:
            pass
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        # try to access non-existent shared mem
        shm = serverMgr.get_shm()
        assert (shm is None)
        # creat memory and check server can access it
        data = "hello world"
        serverMgr.create_shm(data)  # create mem and assign it data
        shm = serverMgr.get_shm()
        assert ("psm_moneoSM" in shm._name)  # the stored name has a slash
        msg = bytes(shm.buf[:11]).decode('utf-8')  # bytes to string
        assert (msg == "hello world")
        serverMgr.delete_shm()


if __name__ == '__main__':
    unittest.main()
