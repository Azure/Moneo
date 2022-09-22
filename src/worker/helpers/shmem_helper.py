from multiprocessing import shared_memory
from multiprocessing import resource_tracker
import sys

"""Moneo Shared Memory Helper"""


def clean_Leaked_shm(shm_name):
    ''' Clean up Resources'''
    shm = shared_memory.SharedMemory(name=shm_name)
    shm.close()
    shm.unlink()


class Shared_Mem_Mngr:
    """Moneo Shared Memory Helper class"""

    def __init__(self, shm_name, isClient=False):
        '''Init, set shm name and type of Access type Client/Server.'''
        self.isClient = isClient
        self.name = shm_name
        self.shmCreated = False

    def create_shm(self, data=None, size=1024):
        '''Create memory of data size or of specified size. If data assign data.'''
        if self.isClient:  # client does not need to create shared mem just retrieve
            shm = self.get_shm()
        else:
            if self.shmCreated:
                self.delete_shm()  # delete old shared memory
            if data:  # If data provided creat shm of size data and assign
                size = len(data.encode("utf8"))
                shm = shared_memory.SharedMemory(
                    create=True, size=size, name=self.name)
                shm.buf[:size] = bytes(data, 'UTF-8')
            else:  # Create shm of specified size
                shm = shared_memory.SharedMemory(
                    create=True, size=size, name=self.name)
        self.shmCreated = True
        return shm

    def delete_shm(self):
        '''Delete shmem'''
        if self.isClient:  # the client should not be destroying memory
            return
        clean_Leaked_shm(self.name)

    def get_shm(self):
        '''Return Shared Memory'''
        if self.isClient:
            try:
                shm = shared_memory.SharedMemory(name=self.name)
                # we need to tell the client process to not destroy memory
                resource_tracker.unregister(shm._name, "shared_memory")
                return shm
            except BaseException:
                return None
        else:
            if not self.shmCreated:
                return None
            else:
                return shared_memory.SharedMemory(name=self.name)
