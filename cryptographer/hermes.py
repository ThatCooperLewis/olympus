from queue import Queue
from threading import Thread
from time import time as now
from typing import List, Tuple

from crosstower.models import Order, Balance
from crosstower.socket_api.private import OrderListener, Trading

'''

- should we hodl when it drops? sell on the way down?
- change amount based on prediction level (including inverse maybe?)
- Include regular check for failed orders

- Need to check total balance of trading account, to determine trade size
- Need to stack compound same-orders to execute opposite once inverse trend is expected
- Fuck this is more complicated than I thought
- Need to make sure there's enough USD when buying, but the trade amount in Order() is exclusively BTC quantity
    - Use certain BTC price in prediction history? Based on how many prediction cycles?
'''

MAX_TRADE_PERCENTAGE = .2
CRYPTO_SYMBOL = 'BTC_TR'
FIAT_SYMBOL = 'USD'
TRADING_SYMBOL = 'BTCUSD_TR'


class PredictionVector:

    # Simple solution for useful queue objects
    def __init__(self, weight, predictions, timestamp):
        self.weight = weight
        self.prediction_history = predictions
        self.timestamp = timestamp


class Hermes:

    '''
    Calculate order amounts based on predictions
    '''

    def __init__(self, override_orderListener=None, override_tradingAccount=None) -> None:
        self.__queue: Queue = Queue()
        self.__thread: Thread = Thread(target=self.__main_loop, args=())

        # Override the API classes if testing
        if override_orderListener:
            self.__order_listener = override_orderListener
        else:
            self.__order_listener = OrderListener()
        if override_tradingAccount:
            self.__trading_account = override_tradingAccount
        else:
            self.__trading_account = Trading()

        # TODO this is a tuple but I treat is like a single Order object. Also this isn't syntactically correct
        self.__last_order: Tuple[Order, PredictionVector] = None
        self.order_history = []
        self.__abort = False

    # Public

    def submit(self, queue_object: PredictionVector):
        '''
        Submit a new PredictionVector to the queue, starting a new order process
        '''
        if type(queue_object) is not PredictionVector:
            raise Exception("What's up guy? Bad type submitted to queue!")
        self.__queue.put(queue_object)

    def start(self):
        '''
        Run in the background, waiting for new ticker submissions
        '''
        self.__order_listener.start()
        self.__thread.start()

    def abort(self):
        '''
        Notify all active threads to end their loops
        '''
        self.__abort = True
        self.__order_listener.end()

    # Private
    def __parse_quantity(self, prediction: PredictionVector, balance: float) -> float:
        percentage = MAX_TRADE_PERCENTAGE * abs(prediction.weight)
        order_quantity = percentage * balance
        return order_quantity

    def __parse_balances(self, balances: List[Balance]) -> Tuple[float, float]:
        for balance in balances:
            if balance.currency == FIAT_SYMBOL:
                fiat_balance = balance.available
            elif balance.currency == CRYPTO_SYMBOL:
                crypto_balance = balance.available
        return crypto_balance, fiat_balance

    def __create_order(self, prediction: PredictionVector, balances: List[Balance]) -> Order:
        crypto_balance, fiat_balance = self.__parse_balances(balances)
        # TODO: There's an issue here.. when the BTC balance is very high and USD low, basic buy orders fail? Because it's trying to buy too much BTC
        # I think buy & sell need to be computed separately
        # But that means we'd have to grab the current BTC price to convert here
        trade_quantity: float = self.__parse_quantity(
            prediction, crypto_balance)
        if prediction.weight > 0:
            side = 'buy'
        elif prediction.weight < 0:
            side = 'sell'
        else:
            return None
        # TODO: maybe incorporate the prediction cycles so this is the actual current price?
        predicted_price = prediction.prediction_history[-4]
        if side == 'buy' and (predicted_price * trade_quantity) > fiat_balance:
            print('UH OH! No money UwU')
            return None
        return Order.create(trade_quantity, side, TRADING_SYMBOL)
        # also check total account balance to determine portion
        pass

    def __create_follower_order(self, last_order: Tuple[Order, PredictionVector], new_prediction: PredictionVector, balances: List[Balance]) -> Order:
        crypto_balance, fiat_balance = self.__parse_balances(balances)
        # trade_quantity = self.__parse_quantity(new_prediction, crypto_balance)
        order = Order(last_order.quantity, '', TRADING_SYMBOL)
        if last_order.side == 'buy':
            order.side = 'buy'  # Continuing trend upwards
            if new_prediction.weight < 0:
                order.side = 'sell'  # Turning down
        elif last_order.side == 'sell':
            order.side = 'sell'  # Continuing trend downwards
            if new_prediction.weight > 0:
                order.side = 'buy'  # Turning up

        # Need to figured out order history stacking
        # That way, as the same trend compounds, the inverse will trigger a full sale of all previous orders in that direction

        # Act on previous order if conditions are ideal
        # IF prediction is same direction, do same order
        #  - track total of all "same orders" in a row
        # ELSE prediction is stagnant or opposite, do inverse order
        #  - inverse order should be same-order total from (a)
        pass

    def __main_loop(self):
        try:
            while not self.__abort:
                if self.__queue.qsize() > 0:
                    prediction: PredictionVector = self.__queue.get()
                    balances = self.__trading_account.get_trading_balance(
                        [CRYPTO_SYMBOL, FIAT_SYMBOL])
                    if self.__last_order:
                        last_order = self.__last_order
                        follower_order = self.__create_follower_order(
                            last_order, prediction)
                        if follower_order:
                            self.__order_listener.submit_order(follower_order)
                    order = self.__create_order(prediction, balances)
                    if order:
                        self.__order_listener.submit_order(order)
                        self.__last_order = order
        except KeyboardInterrupt:
            self.abort()


'''
get trading balance (both BTC and USD)
get prediction vector
use 

'''
