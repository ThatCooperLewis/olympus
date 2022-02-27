
import json
import os
import uuid
from crosstower.models import Ticker, Order

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

def get_basic_ticker() -> Ticker:
    return Ticker({
        'symbol': 'BTCUSD',
        'timestamp': '2010-01-01T00:00:00.000Z',
        'bid': '1',
        'ask': '2',
        'last': '3',
        'volume': '4',
        'volumeQuote': '5',
        'high': '6',
        'low': '7',
        'open': '8'
    })

def get_basic_order() -> Order:
    return Order({
        'symbol': 'BTCUSD',
        'timestamp': '2010-01-01T00:00:00.000Z',
        'quantity': '1',
        'side': 'BUY',
        'status': 'QUEUED'
    })