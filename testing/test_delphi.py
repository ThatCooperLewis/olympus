from unittest import TestCase
import unittest
from time import sleep
from cryptographer import Delphi
import testing.utils as utils
from queue import Queue
from threading import Thread

class TestDelphi(TestCase):

    def setUp(self):
        self.delphi = Delphi(
            csv_path='testing/test_files/test_data.csv',
            model_path='testing/test_files/test_model.h5',
            params_path='testing/test_files/test_params.json',
            iteration_length=3
        )

    def tearDown(self):
        self.delphi = None
        utils.delete_file('testing/test_files/test_data_tmp.csv')

    def test_init(self):
        self.assertEqual(self.delphi.csv_path, 'testing/test_files/test_data.csv')
        self.assertEqual(self.delphi.tmp_csv_path, 'testing/test_files/test_data_tmp.csv')
        self.assertEqual(self.delphi.iterations, 3)
        self.assertEqual(self.delphi.abort, False)
        self.assertEqual(self.delphi.predictor.csv_path, 'testing/test_files/test_data_tmp.csv')
        self.assertEqual(self.delphi.seq_len, 18)
        self.assertEqual(self.delphi.delta_threshold, 0.0003)

    def test_run_loop(self):
        queue = Queue()
        thread = Thread(target=self.delphi.run_loop, args=(queue,))
        thread.start()
        # Wait for the queue to fill up.
        for i in range(5):
            sleep(5)
            if queue.qsize() > 0:
                break
        self.assertTrue(queue.qsize() > 0)
        self.delphi.abort = True
        thread.join()
        sleep(5)
        self.assertEqual(utils.count_rows_from_file(self.delphi.tmp_csv_path), 104)