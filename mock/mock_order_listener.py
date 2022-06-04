from time import sleep

from olympus.hermes import Hermes
from utils import DiscordWebhook, Logger
from utils.postgres import Postgres

from mock.mock_api import MockAPI


class MockOrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.mock_api = MockAPI()
        self.hermes = Hermes(
            override_orderListener=self.mock_api.listener,
            override_tradingAccount=self.mock_api.trading
        )
        self.postgres = Postgres(order_table_override='_mock_order_feed')
        self.hermes.postgres = self.postgres
        self.abort = False

    def run(self):
        self.discord.send_status(f"MockOrderListener has started a new run. (Git hash: `{Logger.git_hash()}`)")
        self.hermes.run()
        try:
            while True:
                sleep(0.2)
        except KeyboardInterrupt:
            self.hermes.stop()
            self.log.debug('KeyboardInterrupt')

if __name__ == '__main__':
    MockOrderListener().run()
