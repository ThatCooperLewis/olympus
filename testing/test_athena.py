from unittest import TestCase
import unittest
from time import sleep
from olympus import Athena
from threading import Thread
import testing.utils as utils 
from crosstower.models import Ticker


class TestAthena(TestCase):

    def setUp(self):
        self.filename = utils.create_blank_file()
        self.athena = Athena(custom_csv_path=self.filename)

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
        self.athena.run(headless=True)
        sleep(5)
        # Test that the file is not empty
        self.assertTrue(utils.count_rows_from_file(self.filename) > 1)
        self.athena.abort = True
        sleep(2)

        # Test that the file is unchanged after quitting
        row_count = utils.count_rows_from_file(self.filename)
        sleep(2)
        self.assertEqual(row_count, utils.count_rows_from_file(self.filename))

    def test_ticker_loop(self):
        thread = Thread(target=self.athena.ticker_loop, daemon=True)
        thread.start()
        sleep(5)
        self.assertTrue(self.athena.queue.qsize() > 0)
        self.athena.abort = True
        thread.join()

    def test_csv_loop(self):
        thread = Thread(target=self.athena.csv_loop)
        thread.start()
        test_ticker = utils.get_basic_ticker()
        self.assertEqual(test_ticker.csv_line, '2.0,1.0,3,7,6,8,4,5,1262332800\n')
        self.athena.queue.put(test_ticker)
        sleep(7)
        self.assertEqual(utils.count_rows_from_file(self.filename), 1)
        self.assertEqual(utils.get_first_row_from_file(self.filename),'2.0,1.0,3,7,6,8,4,5,1262332800\n')
        self.athena.abort = True
        thread.join()

    def test_superclass(self):
        self.athena.run(headless=True)
        sleep(2)
        self.athena.join_threads()
        sleep(5)
        for thread in self.athena.all_threads:
            self.assertFalse(thread.is_alive())

    def test_restart_and_stop(self):
        self.athena.run(headless=True)
        sleep(3)
        old = utils.count_rows_from_file(self.filename)
        self.athena.restart_socket()
        sleep(3)
        new = utils.count_rows_from_file(self.filename)
        self.assertNotEqual(old, new)
        self.athena.stop()
        sleep(5)
        for thread in self.athena.all_threads:
            self.assertFalse(thread.is_alive())

if __name__ == '__main__':
    unittest.main()