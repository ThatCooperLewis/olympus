import uuid
from cgi import test
from time import time as now
from unittest import TestCase
from unittest.mock import Mock

from mock import MockDiscord

import testing.config as constants
from testing.utils import PostgresTesting
from testing import utils

class TestPostgres(TestCase):

    def setUp(self):
        # TODO: This is dangerous. Make a separate DB for testing.
        self.postgres: PostgresTesting = PostgresTesting.setUp()
        self.postgres.discord = MockDiscord('Postgres')
    
    def tearDown(self):
        self.postgres.tearDown()
        self.postgres.conn.close()
        self.postgres = None
    
    def test_init(self):
        self.assertEqual(self.postgres.conn.closed, False)
        self.assertEqual(self.postgres.conn.autocommit, False)
        self.assertEqual(self.postgres.ticker_table_name, constants.POSTGRES_TEST_TICKER_TABLE)
        self.assertEqual(self.postgres.order_table_name, constants.POSTGRES_TEST_ORDER_TABLE)
        self.assertEqual(self.postgres.prediction_table_name, constants.POSTGRES_TEST_PREDICTION_TABLE)

    def test_insert_ticker(self):
        ticker = utils.get_basic_ticker()
        self.postgres.insert_ticker(ticker)
        rows = self.postgres.get_latest_tickers(1)
        self.assertEqual(len(rows), 12)
        first_ticker = rows[0]
        self.assertEqual(first_ticker.timestamp, ticker.timestamp)
        self.assertEqual(first_ticker.ask, ticker.ask)
        self.assertEqual(self.postgres.conn.closed, False)

    def test_insert_order(self):
        order = utils.get_basic_order()
        self.postgres.insert_order(order)
        rows = self.postgres.get_queued_orders()
        self.assertEqual(len(rows), 1)
        first_order = rows[0]
        self.assertAlmostEqual(first_order.timestamp, int(now()), delta=3)
        self.assertEqual(first_order.quantity, order.quantity)
        self.assertEqual(first_order.side, order.side)
        self.assertEqual(first_order.status, 'QUEUED')
        self.assertEqual(first_order.uuid, order.uuid)

    def test_insert_prediction(self):
        prediction = utils.get_basic_prediction()
        self.postgres.insert_prediction_vector(prediction)
        rows = self.postgres.get_queued_predictions()
        self.assertEqual(len(rows), 1)
        first_prediction = rows[0]
        self.assertAlmostEqual(first_prediction.timestamp, int(now()), delta=3)
        self.assertEqual(first_prediction.prediction_timestamp, prediction.timestamp)
        self.assertEqual(first_prediction.weight, prediction.weight)
        self.assertEqual(first_prediction.uuid, prediction.uuid)
        self.assertEqual(first_prediction.status, 'QUEUED')
        self.assertEqual(str(first_prediction.prediction_history[0]), str(prediction.prediction_history[0]))

    def test_query_and_get_latest_tickers(self):
        for i in range(0, 10):
            query =  f"""INSERT INTO {constants.POSTGRES_TEST_TICKER_TABLE} (timestamp, ask, bid, last, low, high, open, volume, volume_quote) 
            VALUES ({i}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)"""
            self.postgres.query(query, fetch_result=False)
        rows = self.postgres.get_latest_tickers(10)
        self.assertEqual(len(rows), 10)
        
    def test_update_order(self):
        order = utils.get_basic_order()
        self.postgres.insert_order(order)
        rows = self.postgres.get_queued_orders()
        self.assertEqual(len(rows), 1)
        self.postgres.update_order_status(order.uuid, 'PROCESSING')
        rows = self.postgres.get_queued_orders()
        self.assertEqual(len(rows), 0)
        
    def test_update_prediction(self):
        prediction = utils.get_basic_prediction()
        self.postgres.insert_prediction_vector(prediction)
        rows = self.postgres.get_queued_predictions()
        self.assertEqual(len(rows), 1)
        self.postgres.update_prediction_status(prediction.uuid, 'COMPLETE')
        rows = self.postgres.get_queued_predictions()
        self.assertEqual(len(rows), 0)
        
