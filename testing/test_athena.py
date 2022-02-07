from unittest import TestCase, TestSuite
import unittest

from cryptographer.athena import Athena


def count_rows_from_file(file_name: str) -> int:
    with open(file_name, 'r') as f:
        return len(f.readlines())

class TestAthena(TestCase):

    def setUp(self):
        self.athena = Athena()

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.athena.connection_attempts, 0)
        self.assertEqual(self.athena.quitting, False)
        self.assertEqual(self.athena.queue.qsize(), 0)
        self.assertEqual(self.athena.last_time, 0)
        self.assertEqual(self.athena.last_line, '')
        self.assertEqual(self.athena.interval, 60)

    def test_restart_socket(self):
        self.athena.restart_socket()
        self.assertEqual(self.athena.connection_attempts, 0)
        self.assertEqual(self.athena.quitting, False)
        self.assertEqual(self.athena.queue.qsize(), 0)
        self.assertEqual(self.athena.last_time, 0)
        self.assertEqual(self.athena.last_line, '')

    def test_get_response(self):
        pass

    def test_subscribe(self):
        pass

    def test_ticker_loop(self):
        pass

    def test_watchdog_loop(self):
        pass

    def test_csv_loop(self):
        pass

    def test_handle_commands(self):
        pass

if __name__ == '__main__':
    unittest.main()