from queue import Queue
from threading import Thread
from time import sleep
from time import time as now
from unittest import TestCase
from mock.mock_discord import MockDiscord

from olympus.delphi import Delphi
from olympus.helper_objects.prediction_queue import \
    PredictionQueueDB as PredictionQueue

import testing.utils as utils
from testing.utils import PostgresTesting
import testing.config as constants

class TestDelphi(TestCase):

    def setUp(self):
        self.postgres = PostgresTesting.setUp()
        self.queue = PredictionQueue(override_postgres=self.postgres)
        self.delphi = Delphi(
            override_model_path='testing/test_files/test_model.h5',
            override_params_path='testing/test_files/test_params.json',
            override_sql_mode_with_csv_path='testing/test_files/test_data.csv',
            override_prediction_queue=self.queue,
            override_iteration_length=3
        )
        self.delphi.interval_size = 3
        self.delphi.discord = MockDiscord('TestDelphi')

    def tearDown(self):
        utils.delete_file(self.delphi.tmp_csv_path)
        self.delphi = None
        self.postgres.tearDown()

    def test_init(self):
        self.assertEqual(self.delphi.csv_path, 'testing/test_files/test_data.csv')
        self.assertEqual(self.delphi.tmp_csv_path[:32], 'testing/test_files/test_data_tmp')
        self.assertEqual(self.delphi.tmp_csv_path[-4:], '.csv')
        self.assertEqual(self.delphi.iterations, 3)
        self.assertFalse(self.delphi.abort)
        self.assertEqual(self.delphi.predictor.csv_path[:32], 'testing/test_files/test_data_tmp')
        self.assertEqual(self.delphi.seq_len, 18)
        self.assertFalse(self.delphi.sql_mode)
        self.assertEqual(self.delphi.delta_threshold, 0.003)

    def test_sql_init(self):
        sql_delphi = Delphi(
            override_model_path='testing/test_files/test_model.h5',
            override_params_path='testing/test_files/test_params.json',
            override_prediction_queue=self.queue,
            override_iteration_length=3
        )
        self.assertTrue(sql_delphi.sql_mode)
        self.assertFalse(sql_delphi.abort)
        self.assertEqual(len(sql_delphi.tmp_csv_path), 23)
        utils.delete_file(sql_delphi.tmp_csv_path)

    def test_run_loop_sql_mode(self):
        self.delphi.sql_mode = True
        self.delphi.postgres = PostgresTesting(
            ticker_table_override=None, # Utilize real tickers
            order_table_override=constants.POSTGRES_TEST_ORDER_TABLE,
            prediction_table_override=constants.POSTGRES_TEST_PREDICTION_TABLE
        )
        self.delphi.run()
        self.__wait_for_queue_to_fill()
        self.assertTrue(self.queue.size > 0)
        self.delphi.stop()
        postgres: PostgresTesting = self.delphi.postgres
        predictions_in_db = postgres.get_queued_predictions()
        prediction = predictions_in_db[0]
        self.assertEqual(len(predictions_in_db), 1)
        self.assertEqual(prediction.status, 'QUEUED')
        self.assertAlmostEqual(prediction.timestamp, int(now()), delta=3)

    def test_superclass(self):
        self.delphi.run()
        sleep(2)
        self.delphi.join_threads()
        sleep(5)
        self.assertFalse(self.delphi.primary_thread.is_alive())

    def __get_first_line_from_file(self, filename: str):
        with open(filename, 'r') as file:
            return file.readline()

    def __wait_for_queue_to_fill(self):
        for i in range(5):
            sleep(3)
            if self.queue.size > 0:
                return
        self.fail("Queue did not fill after 15 seconds")