import unittest
import os
import sys

p = os.path.abspath('../src/worker/helpers')
sys.path.insert(1, p)
from shmem_helper import clean_Leaked_shm
from shmem_helper import Shared_Mem_Mngr

"""Moneo Shared Memory test"""


def cleanUp(shm_name):
    """clean up rogue shared memory"""
    try:
        # in the event of a previous unclean exit. Clean up leaked resouces
        clean_Leaked_shm(shm_name)
    except FileNotFoundError:
        pass


class SharedMemTestCase(unittest.TestCase):
    """Shared Mem unit test Class."""

    def test_client_class(self):
        """test if client access read memory"""
        cleanUp("psm_moneoSM")
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
        msg = bytes(shm.buf[:shm._size]).decode('utf-8')  # bytes to string
        assert (msg == "hello world")
        serverMgr.delete_shm()

    def test_server_class(self):
        """test if server access read memory"""
        cleanUp("psm_moneoSM")
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        # try to access non-existent shared mem
        shm = serverMgr.get_shm()
        assert (shm is None)
        # creat memory and check server can access it
        data = "hello world"
        serverMgr.create_shm(data)  # create mem and assign it data
        shm = serverMgr.get_shm()
        assert ("psm_moneoSM" in shm._name)  # the stored name has a slash
        msg = bytes(shm.buf[:shm._size]).decode('utf-8')  # bytes to string
        assert (msg == "hello world")
        serverMgr.delete_shm()

    def test_resize(self):
        """Test resize of shared memory"""
        cleanUp("psm_moneoSM")
        serverMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=False)
        clientMgr = Shared_Mem_Mngr("psm_moneoSM", isClient=True)
        msg1 = 'Not Resized'
        serverMgr.create_shm(msg1)  # create mem and assign it data
        shm = clientMgr.get_shm()
        msg = bytes(shm.buf[:shm._size]).decode('utf-8')
        initial_size = shm._size
        assert (msg == msg1)  # check contents
        msg2 = msg1 + " more size"
        clientMgr.resize_shm(data=msg2)
        shm = clientMgr.get_shm()
        shm_server = serverMgr.get_shm()
        assert (shm._size == shm_server._size)  # check resize
        assert (shm._size > initial_size)  # check resize
        msg = bytes(shm.buf[:shm._size]).decode('utf-8')
        assert (msg == msg2)  # check contents
        msg = bytes(shm_server.buf[:shm._size]).decode('utf-8')
        assert (msg == msg2)  # check contents
        serverMgr.delete_shm()


if __name__ == '__main__':
    unittest.main()
