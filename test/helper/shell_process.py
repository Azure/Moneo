import subprocess



def shell_cmd(args):
    """Helper Function for running subprocess"""
    child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        result, errs = child.communicate(timeout=60)
    except TimeoutExpired:
        child.kill()
        result, errs = child.communicate()
    return result.decode()
