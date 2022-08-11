from pathlib import Path
import json


def load_data(filepath):
    """Helper Function for loading file"""
    data=None
    with Path(filepath).open() as fp:
        data = fp.read()
    return  data

def jsonToDict(filepath: str):
        with open(filepath) as response_data_file:
            response_data = json.load(response_data_file)
        return response_data
