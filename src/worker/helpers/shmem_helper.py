from multiprocessing import shared_memory
from multiprocessing import resource_tracker
import sys


class Shared_Mem_Mngr:
    def __init__(self, shm_name, isClient=False):
        self.isClient = isClient
        self.name = shm_name
        self.shm = None

    def create_shm(self, data=None, size=None):
        if self.isClient:  # client does not need to create shared mem just retrieve
            shm = self.get_shm()
        else:
            if self.shm:
                self.delete_shm()  # delete old shared memory
            if data:
                size = sys.getsizeof(data)
            else:
                shm = shared_memory.SharedMemory(create=True, size=size, name=self.name)
        print(shm.name)
        self.shm = shm
        return shm

    def delete_shm(self):
        if self.isClient:  # the client should not be destroying memory
            return
        self.shm.close()
        self.shm.unlink()

    def get_shm(self):
        if not self.shm:
            print('Shared memory has not been created/retrieved')
        else:
            if self.isClient:
                shm = shared_memory.SharedMemory(name=self.name)
                resource_tracker.unregister(shm._name, "shared_memory")  # we need to tell the client process to not destroy memory
                return shm
            else:
                return self.shm
