
from cgi import test
import json
import os
import uuid
from crosstower.models import Ticker, Order
from olympus.helper_objects import PredictionVector
from utils import Postgres
import testing.config as constants

class PostgresTesting(Postgres):

    # Expose query method for testing
    def query(self, query_str: str, fetch_result: bool):
        return self._query(query_str, fetch_result)
    
    def tearDown(self):
        self._query(f'DELETE FROM {constants.POSTGRES_TEST_ORDER_TABLE}', fetch_result=False)
        self._query(f'DELETE FROM {constants.POSTGRES_TEST_PREDICTION_TABLE}', fetch_result=False)
        self._query(f'DELETE FROM {constants.POSTGRES_TEST_TICKER_TABLE}', fetch_result=False)
    
    @classmethod
    def setUp(cls):
        postgres = cls(
            ticker_table_override=constants.POSTGRES_TEST_TICKER_TABLE,
            order_table_override=constants.POSTGRES_TEST_ORDER_TABLE,
            prediction_table_override=constants.POSTGRES_TEST_PREDICTION_TABLE
        )
        # Clear any possible leftover data
        postgres.tearDown()
        return postgres

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

def delete_all_test_files():
    exclude = [
        'test_data.csv',
        'test_params.json',
        'test_model.h5'
    ]
    testing_dirs = [
        './testing',
        './testing/test_files',
    ]
    for dir in testing_dirs:
        for filename in os.listdir(dir):
            if filename not in exclude and filename.startswith('test_') and (filename.endswith(('.csv', '.json'))):
                os.remove(dir + '/' + filename)

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
    }, uuid=uuid.uuid4().hex)

def get_basic_prediction() -> PredictionVector:
    return PredictionVector(
        weight=-1,
        predictions=[
            46842.47,
            46842.47,
            46842.47,
            46842.47,
            46842.47,
            46400.00
        ],
        timestamp=123467890
    )