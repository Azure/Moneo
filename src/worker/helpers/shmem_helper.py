from multiprocessing import shared_memory
from multiprocessing import resource_tracker
import sys


def clean_Leaked_shm(shm_name):
    ''' Clean up Resources'''
    shm = shared_memory.SharedMemory(name=shm_name)
    shm.close()
    shm.unlink()


class Shared_Mem_Mngr:
    def __init__(self, shm_name, isClient=False):
        self.isClient = isClient
        self.name = shm_name
        self.shm = None

    def create_shm(self, data=None, size=1024):
        if self.isClient:  # client does not need to create shared mem just retrieve
            shm = self.get_shm()
        else:
            if self.shm:
                self.delete_shm()  # delete old shared memory
            if data:
                size = len(data.encode("utf8"))
                shm = shared_memory.SharedMemory(create=True, size=size, name=self.name)
                shm.buf[:size]=bytes(data,'UTF-8')
            else:
                shm = shared_memory.SharedMemory(create=True, size=size, name=self.name)
        self.shm = shm
        return shm

    def delete_shm(self):
        if self.isClient:  # the client should not be destroying memory
            return
        clean_Leaked_shm(self.name)

    def get_shm(self):
        if self.isClient:
            try:
                shm = shared_memory.SharedMemory(name=self.name)
                resource_tracker.unregister(shm._name, "shared_memory")  # we need to tell the client process to not destroy memory
                return shm
            except:
                return None
        else:
            if not self.shm:
                return None
            else:
                return self.shm
    