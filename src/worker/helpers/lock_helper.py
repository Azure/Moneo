from filelock import FileLock


class file_lock_mgr():
    def __init__(self, lockPath, _timeout=5):
        self.lock = FileLock(lockPath, timeout=_timeout)

    def acquire(self):
        retry = 0
        while retry < 3:
            try:
                self.lock.acquire()
                break
            except BaseException:  # try 3 times
                retry = retry + 1
        if retry >= 3:
            raise Exception(
                "Failed to update job. Could not aquire lock for shared memory"
                )

    def release(self):
        self.lock.release()
