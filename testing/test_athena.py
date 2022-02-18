from unittest import TestCase
import unittest
from time import sleep
from cryptographer import Athena
from threading import Thread
import testing.utils as utils 
from crosstower.models import Ticker


class TestAthena(TestCase):

    def setUp(self):
        self.athena = Athena()

    def tearDown(self):
        self.athena = None

    def test_init(self):
        self.assertEqual(self.athena.connection_attempts, 0)
        self.assertEqual(self.athena.abort, False)
        self.assertEqual(self.athena.queue.qsize(), 0)
        self.assertEqual(self.athena.symbol, 'BTCUSD')
        self.assertEqual(self.athena.interval, 1)

    def test_run_and_exit(self):
        filename = utils.create_blank_file()
        self.athena.run(
            csv_path=filename,
            headless=True
        )
        sleep(5)
        # Test that the file is not empty
        self.assertTrue(utils.count_rows_from_file(filename) > 1)
        self.athena.abort = True
        sleep(2)

        # Test that the file is unchanged after quitting
        row_count = utils.count_rows_from_file(filename)
        sleep(2)
        self.assertEqual(row_count, utils.count_rows_from_file(filename))
        utils.delete_file(filename)

    def test_ticker_loop(self):
        thread = Thread(target=self.athena.ticker_loop, daemon=True).start()
        sleep(5)
        self.assertTrue(self.athena.queue.qsize() > 0)
        self.athena.abort = True

    def test_csv_loop(self):
        filename = utils.create_blank_file()
        Thread(target=self.athena.csv_loop, args=(filename,)).start()
        test_ticker = Ticker({
            'symbol': 'BTCUSD',
            'timestamp': '2019-01-01T00:00:00.000Z',
            'bid': '1',
            'ask': '2',
            'last': '3',
            'volume': '4',
            'high': '5',
            'low': '6',
            'open': '7'
        })
        self.assertEqual(test_ticker.csv_line, '2.0,1.0,3,6,5,7,4,None,1546329600\n')
        self.athena.queue.put(test_ticker)
        sleep(7)
        self.assertEqual(utils.count_rows_from_file(filename), 1)
        self.assertEqual(utils.get_first_row_from_file(filename),'2.0,1.0,3,6,5,7,4,None,1546329600\n')
        self.athena.quitting = True
        utils.delete_file(filename)



if __name__ == '__main__':
    unittest.main()