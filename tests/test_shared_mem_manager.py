import unittest
import os
import sys

p = os.path.abspath('../src/worker/helpers')
sys.path.insert(1, p)
from shmem_helper import Shared_Mem_Mngr
from shmem_helper import clean_Leaked_shm

"""Moneo Shared Memory test"""


class SharedMemTestCase(unittest.TestCase):
    """Shared Mem unit test Class."""

    def test_client_class(self):
        """test if client access read memory"""
        try:
            clean_Leaked_shm("psm_moneoSM")
        except:
            pass
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        clientMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=True)
        # try to access non-existent shared mem
        shm = clientMgr.get_shm()
        assert (shm == None)
        # creat memory and check server can access it        
        data = "hello world"
        serverMgr.create_shm(data)
        shm = clientMgr.get_shm()
        assert (shm._name == "/psm_moneoSM")
        msg = bytes(shm.buf[:11]).decode('utf-8')
        assert ( msg == "hello world")
        serverMgr.delete_shm()

    def test_server_class(self):
        """test if server access read memory"""
        try:
            clean_Leaked_shm("psm_moneoSM")
        except:
            pass
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        # try to access non-existent shared mem
        shm = serverMgr.get_shm()
        assert (shm == None)
        # creat memory and check server can access it
        data = "hello world"
        serverMgr.create_shm(data) 
        shm = serverMgr.get_shm()
        assert (shm._name == "/psm_moneoSM")
        msg = bytes(shm.buf[:11]).decode('utf-8')
        assert ( msg == "hello world")
        serverMgr.delete_shm()


if __name__ == '__main__':
    unittest.main()
