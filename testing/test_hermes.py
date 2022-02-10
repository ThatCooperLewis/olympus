from time import sleep
from unittest import TestCase

from cryptographer.hermes import Hermes, PredictionVector
from mock import MockCrosstowerAPI as MockAPI

from testing import utils


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

    def tearDown(self):
        self.hermes = None
        utils.delete_file(self.params_file)

    def test_init(self):
        self.assertFalse(self.hermes.abort, False)
        self.assertEqual(self.hermes.order_listener, self.mock_api.listener)
        self.assertEqual(self.hermes.trading_account, self.mock_api.trading)

    def test_submit(self):
        self.hermes.start()
        self.hermes.submit_prediction_to_queue(PredictionVector(
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
        ))
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

    # TODO: Add stacking order test
