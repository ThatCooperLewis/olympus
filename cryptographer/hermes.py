from queue import Queue
from threading import Thread
from time import time as now
from typing import List

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

    def __init__(self) -> None:
        self.__queue: Queue = Queue()
        self.__thread: Thread = Thread(target=self.__main_loop, args=())
        self.__order_listener = OrderListener()
        self.__trading_account = Trading()
        self.__last_order = (Order, PredictionVector)

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

    def __create_order(self, prediction: PredictionVector, balances: List[Balance]) -> Order:
        crypto_balance = None
        fiat_balance = None
        for balance in balances:
            if balance.currency == FIAT_SYMBOL:
                fiat_balance = balance.available
            elif balance.available == CRYPTO_SYMBOL:
                crypto_balance = balance.available
        if prediction.weight > 0:
            trade_percentage = MAX_TRADE_PERCENTAGE * prediction.weight
            side = 'buy'
        elif prediction.weight < 0:
            trade_percentage = MAX_TRADE_PERCENTAGE * abs(prediction.weight)
            side = 'sell'
        else:
            return None
        trade_quantity = crypto_balance * trade_percentage
        # TODO: maybe incorporate the prediction cycles so this is the actual current price?
        predicted_price = prediction.prediction_history[-4]
        if side == 'buy' and (predicted_price * trade_quantity) > fiat_balance:
            print('UH OH! No money UwU')
            return None
        return Order.create(trade_quantity, side, TRADING_SYMBOL) 
        # also check total account balance to determine portion
        pass

    def __create_follower_order(self, last_order: Order, new_prediction: PredictionVector) -> Order:
        # Act on previous order if conditions are ideal
        # IF prediction is same direction, do same order
        #  - track total of all "same orders" in a row
        # ELSE prediction is stagnant or opposite, do inverse order
        #  - inverse order should be same-order total from (a)
        pass

    def __main_loop(self):
        try:
            while not self.__abort:
                if self.__queue.qsize():
                    prediction: PredictionVector = self.__queue.get()
                    balances = self.__trading_account.get_trading_balance([CRYPTO_SYMBOL, FIAT_SYMBOL])
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
