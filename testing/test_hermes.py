from time import sleep
from unittest import TestCase

from mock import MockCrosstowerAPI as MockAPI
from mock import MockDiscord
from olympus import Hermes
from olympus.utils import PredictionVector

from testing import config, utils
from testing.utils import PostgresTesting


class TestHermes(TestCase):

    def setUp(self):
        self.params_file = utils.save_as_json([
            {
                "currency": "USD",
                "available": 25000.0
            },
            {
                "currency": "BTC_TR",
                "available": 5
            }
        ])
        self.mock_api = MockAPI(self.params_file)
        self.hermes = Hermes(
            override_orderListener=self.mock_api.listener,
            override_tradingAccount=self.mock_api.trading
        )
        self.hermes.discord = MockDiscord('Postgres')
        self.hermes.postgres = PostgresTesting(
            ticker_table_override=config.POSTGRES_TEST_TICKER_TABLE, 
            order_table_override=config.POSTGRES_TEST_ORDER_TABLE,
            prediction_table_override=config.POSTGRES_TEST_PREDICTION_TABLE
        )

    def tearDown(self):
        postgres: PostgresTesting = self.hermes.postgres
        postgres.query(f'DELETE FROM {config.POSTGRES_TEST_ORDER_TABLE}', fetch_result=False)
        self.hermes = None
        utils.delete_file(self.params_file)

    def test_init(self):
        self.assertFalse(self.hermes.abort, False)
        self.assertEqual(self.hermes.order_listener, self.mock_api.listener)
        self.assertEqual(self.hermes.trading_account, self.mock_api.trading)

    def test_submit(self):
        self.hermes.start()
        self.hermes.submit_prediction_to_queue(utils.get_basic_prediction())
        sleep(5)
        self.hermes.stop()
        balances = utils.get_json_from_file(self.params_file)
        self.assertEqual(balances[1]['currency'], "BTC_TR")
        self.assertEqual(balances[1]['available'], 4.0)

    def test_run(self):
        self.hermes.start()
        self.assertEqual(self.hermes.abort, False)
        self.hermes.stop()
        self.assertEqual(self.hermes.abort, True)

    def test_order_status_update(self):
        self.hermes.start()
        prediction = utils.get_basic_prediction()
        self.hermes.submit_prediction_to_queue(prediction)
        sleep(5)
        self.hermes.stop()
        order_rows = self.hermes.postgres.get_outstanding_orders()
        self.assertEqual(len(order_rows), 0)
        test_postgres: PostgresTesting = self.hermes.postgres
        completed_rows = test_postgres.query(f"SELECT * FROM {config.POSTGRES_TEST_ORDER_TABLE} WHERE status = 'COMPLETE'", fetch_result=True)
        self.assertEqual(len(completed_rows), 1)
        self.assertEqual(completed_rows[0][4], prediction.uuid)

    # TODO: Add stacking order test
