from pathlib import Path



def load_data(filepath):
    """Helper Function for loading file"""
    data=None
    with Path(filepath).open() as fp:
        data = fp.read()
    return  data
