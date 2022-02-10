
import json
import os
import uuid


def count_rows_from_file(file_name: str) -> int:
    with open(file_name, 'r') as f:
        return len(f.readlines())

def create_blank_file() -> None:
    file_name = 'testing/test_' + str(uuid.uuid4()) + '.csv'
    with open(file_name, 'w') as f:
        f.write('')
    return file_name

def delete_file(file_name: str) -> None:
    try:
        os.remove(file_name)
    except:
        pass

def get_first_row_from_file(file_name: str) -> str:
    with open(file_name, 'r') as f:
        return f.readline()

def save_as_json(list: list) -> None:
    file_name = 'testing/test_' + str(uuid.uuid4()) + '.json'
    with open(file_name, 'w') as f:
        f.write(json.dumps(list))
    return file_name

def get_json_from_file(file_name: str) -> list:
    with open(file_name, 'r') as f:
        return json.loads(f.read())
