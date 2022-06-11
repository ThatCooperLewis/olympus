from unittest import TestCase
import unittest
from time import sleep
from olympus.athena import Athena
from threading import Thread
import testing.utils as utils
import testing.config as constants
from crosstower.models import Ticker
from mock import MockDiscord

class TestAthena(TestCase):

    def setUp(self):
        self.filename = utils.create_blank_file()
        self.athena = Athena(custom_csv_path=self.filename)
        self.athena.discord = MockDiscord('TestAthena')

    def tearDown(self):
        self.athena = None
        utils.delete_file(self.filename)

    def test_init(self):
        self.assertEqual(self.athena.connection_attempts, 0)
        self.assertEqual(self.athena.abort, False)
        self.assertEqual(self.athena.queue.qsize(), 0)
        self.assertEqual(self.athena.symbol, 'BTCUSD')
        self.assertEqual(self.athena.interval, 1)

    def test_run_and_exit(self):
        self.athena.timeout_threshold = 10
        self.athena.run()
        sleep(20)
        # Test that the file is not empty
        self.assertTrue(utils.count_rows_from_file(self.filename) > 1)
        self.athena.abort = True
        sleep(2)
        # Test that the file is unchanged after quitting
        row_count = utils.count_rows_from_file(self.filename)
        sleep(1)
        self.assertEqual(row_count, utils.count_rows_from_file(self.filename))

    def test_ticker_loop(self):
        thread = Thread(target=self.athena.ticker_loop, daemon=True)
        thread.start()
        sleep(5)
        self.assertTrue(self.athena.queue.qsize() > 0)
        self.athena.abort = True
        thread.join()
        
    def test_sql_loop(self):
        self.athena.csv_path = None
        self.athena.postgres = utils.PostgresTesting.setUp()
        thread = Thread(target=self.athena.sql_loop)
        thread.start()
        test_ticker = utils.get_basic_ticker()
        self.athena.queue.put(test_ticker)
        sleep(3)
        result = self.athena.postgres.get_latest_tickers(1)[0]
        self.assertEqual(result.timestamp, test_ticker.timestamp)
        self.athena.abort = True
        thread.join()
        self.athena.postgres.tearDown()
        self.athena.postgres = None
        self.athena.csv_path = self.filename

    def test_superclass(self):
        self.athena.run()
        sleep(2)
        self.athena.join_threads()
        sleep(25)
        for thread in self.athena.all_threads:
            self.assertFalse(thread.is_alive())

    def test_restart_and_stop(self):
        self.athena.run()
        sleep(2)
        old = utils.count_rows_from_file(self.filename)
        self.athena.restart_socket()
        sleep(2)
        new = utils.count_rows_from_file(self.filename)
        self.assertNotEqual(old, new)
        self.athena.stop()
        sleep(20)
        for thread in self.athena.all_threads:
            self.assertFalse(thread.is_alive())

if __name__ == '__main__':
    unittest.main()