import subprocess


def shell_cmd(args, timeout):
    """Helper Function for running subprocess"""
    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        result, errs = child.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        child.kill()
        print("Command " + " ".join(args) + ", Failed on timeout")
        result = 'TimeOut'
        return result
    return result.decode()
