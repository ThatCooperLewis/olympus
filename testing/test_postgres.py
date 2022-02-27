from unittest import TestCase
from unittest.mock import Mock

from utils import PostgresTesting
from testing import utils
from mock import MockDiscord

POSTGRES_TEST_TICKER_TABLE = '_ticker_feed_testing'

class TestPostgres(TestCase):

    def setUp(self):
        # TODO: This is dangerous. Make a separate DB for testing.
        self.postgres: PostgresTesting = PostgresTesting(ticker_table_override=POSTGRES_TEST_TICKER_TABLE)
        self.postgres.discord = MockDiscord('Postgres')
    
    def tearDown(self):
        self.postgres.query(f'DELETE FROM {POSTGRES_TEST_TICKER_TABLE}', fetch_result=False)
        self.postgres.conn.close()
        self.postgres = None
    
    def test_init(self):
        self.assertEqual(self.postgres.conn.closed, False)
        self.assertEqual(self.postgres.conn.autocommit, False)
        self.assertEqual(self.postgres.ticker_table_name, POSTGRES_TEST_TICKER_TABLE)

    def test_insert(self):
        ticker = utils.get_basic_ticker()
        self.postgres.insert_ticker(ticker)
        rows = self.postgres.get_latest_rows(1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], ticker.timestamp)
        self.assertEqual(rows[0][1], ticker.ask)
        self.assertEqual(self.postgres.conn.closed, False)

    def test_query_and_get_latest_rows(self):
        for i in range(0, 10):
            query =  f"""INSERT INTO {POSTGRES_TEST_TICKER_TABLE} (timestamp, ask, bid, last, low, high, open, volume, volume_quote) 
            VALUES ({i}, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)"""
            self.postgres.query(query, fetch_result=False)
        rows = self.postgres.get_latest_rows(10)
        self.assertEqual(len(rows), 10)
        