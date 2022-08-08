import json

def jsonToDict(filepath: str):
        with open(filepath) as response_data_file:
            response_data = json.load(response_data_file)
        return response_data