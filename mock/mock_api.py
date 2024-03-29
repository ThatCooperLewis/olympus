from crosstower.socket_api.private import OrderListener
from typing import List

from crosstower.models import Balance
from utils.config import TradingConfig
from utils import Postgres, Logger, DiscordWebhook
from websockets import connect as Connection
from requests import get

class MockTrading:

    def __init__(self, postgres: Postgres) -> None:
        self.postgres = postgres

    def get_trading_balance(self, currencies: list = []) -> List[Balance]:
        usd_amount, btc_amount = self.postgres.get_latest_mock_balances()
        usd_balance = Balance({'currency': TradingConfig.FIAT_SYMBOL, 'available': usd_amount})
        btc_balance = Balance({'currency': TradingConfig.CRYPTO_SYMBOL, 'available': btc_amount})
        return [usd_balance, btc_balance]


class MockSocket:

    '''
    Used to execute mock orders. Makes changes to _mock_order_feed Postgres table based on order data & current BTC price. 
    Conforms to `crosstower.socket_api.SocketAPI`
    '''

    def __init__(self, postgres: Postgres, trading: MockTrading) -> None:
        self.postgres: Postgres = postgres
        self.trading: MockTrading = trading
        self.discord = DiscordWebhook(__name__)
        self.log = Logger.setup(__name__)
        self.log.debug("Initialized mock socket")
        return

    async def request(self, socket: Connection, method: str, params: dict, uuid: str):
        self.log.debug(f"Request received: {params}")
        if method != 'newOrder':
            raise NotImplementedError
        
        resp = get(f"https://api.crosstower.com/api/2/public/ticker/BTCUSD")
        latest_price = float(resp.json()['ask'])
        side = params['side']
        btc_quantity: float = float(params['quantity'])
        usd_quantity = btc_quantity * latest_price
        
        if side == 'buy':
            usd_quantity *= -1
        elif side == 'sell':
            btc_quantity *= -1
        else:
            raise Exception("Unrecognized order type, expected 'buy' or 'sell'")

        starting_usd, starting_btc = self.trading.get_trading_balance()

        ending_usd = starting_usd.available + usd_quantity
        ending_btc = starting_btc.available + btc_quantity

        total_value = round((ending_usd + ending_btc * latest_price), 2)
        
        if ending_usd <= 0 or ending_btc <= 0:
            self.discord.send_alert("Mock order would result in negative balance. Aborting this order...")
            self.log.error("Zero balance! Skipping order!")
            return

        self.log.debug(f"Submitting mock order: {side}, {btc_quantity} BTC, {usd_quantity} USD")

        self.postgres.insert_mock_order(
            quantity=btc_quantity,
            side=side,
            ending_usd_balance=ending_usd,
            ending_btc_balance=ending_btc,
            current_btc_price=latest_price,
            total_value=total_value,
            uuid=uuid
        )
        
        self.log.debug('Mock order submitted')
        return True

    async def get_authenticated_socket(self):
        return None


class MockAPI:

    '''
    Barebones mock class for mocking account balance and trade orders via postgres.
    '''

    def __init__(self) -> None:
        postgres = Postgres()
        self.trading = MockTrading(postgres)
        self.listener = OrderListener(websocket_override=MockSocket(postgres, self.trading))
        return
