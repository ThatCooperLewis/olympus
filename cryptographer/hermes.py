from queue import Queue
from threading import Thread
from time import time as now
from typing import List, Tuple

from crosstower.models import Order, Balance
from crosstower.socket_api.private import OrderListener, Trading
from utils import Logger
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

    def __init__(self, override_orderListener: OrderListener = None, override_tradingAccount: Trading = None, override_predictionQueue: Queue = None) -> None:
        self.log = Logger.setup(__name__)
        self.abort = False
        self.__orders = []
        self.__thread: Thread = Thread(target=self.__main_loop, args=())

        if override_orderListener:
            self.log.debug('Overriding order listener')
            self.order_listener = override_orderListener
        else:
            self.order_listener = OrderListener()

        if override_tradingAccount:
            self.log.debug('Overriding trading account')
            self.trading_account = override_tradingAccount
        else:
            self.trading_account = Trading()

        if override_predictionQueue:
            self.__queue = override_predictionQueue
        else:
            self.__queue = Queue()

    # Public

    def start(self):
        '''
        Run in the background, waiting for new ticker submissions
        '''
        self.log.debug('Starting Hermes...')
        self.order_listener.start()
        self.__thread.start()

    def stop(self):
        '''
        Notify all active threads to end their loops
        '''
        self.log.debug('Stopping Hermes...')
        self.abort = True
        self.order_listener.end()

    def submit_prediction_to_queue(self, queue_object: PredictionVector):
        '''
        Submit a new PredictionVector to the queue, starting a new order process
        '''
        if type(queue_object) is not PredictionVector:
            self.log.error('Tried to submit non-PredictionVector to queue')
            raise Exception("What's up guy? Bad type submitted to queue!")
        self.__queue.put(queue_object)

    # Private

    def __parse_quantity(self, prediction: PredictionVector, balance: float) -> float:
        '''
        Given a prediction vector, a balance, and a maximum trade percentage, return the quantity of the
        prediction vector to buy or sell

        :param prediction: The prediction vector for the current time step
        :type prediction: PredictionVector
        :param balance: The amount of money you have to spend on the trade
        :type balance: float
        :return: The quantity of the asset to be traded.
        '''
        self.log.debug('Parsing quantity for prediction vector: {}'.format(prediction))
        percentage = MAX_TRADE_PERCENTAGE * abs(prediction.weight)
        order_quantity = percentage * balance
        return order_quantity

    def __parse_balances(self, balances: List[Balance]) -> Tuple[float, float]:
        '''
        Returns the available crypto and fiat balances.

        :param balances: List[Balance]
        :type balances: List[Balance]
        :return: The balances of crypto and fiat.
        '''
        for balance in balances:
            if balance.currency == FIAT_SYMBOL:
                fiat_balance = balance.available
            elif balance.currency == CRYPTO_SYMBOL:
                crypto_balance = balance.available
        return crypto_balance, fiat_balance

    def __create_order(self, prediction: PredictionVector, balances: List[Balance]) -> Order:
        crypto_balance, fiat_balance = self.__parse_balances(balances)
        # TODO: There's an issue here.. when the BTC balance is very high and USD low, basic buy orders fail, because it's trying to buy too much BTC
        # I think buy & sell need to be computed separately
        # But that means we'd have to grab the current BTC price to convert here
        trade_quantity: float = self.__parse_quantity(
            prediction, crypto_balance)
        if prediction.weight > 0:
            side = 'buy'
        elif prediction.weight < 0:
            side = 'sell'
        else:
            self.log.debug('Prediction weight is 0, not executing order')
            return None
        # TODO: maybe incorporate the prediction cycles so this is the actual current price?
        predicted_price = prediction.prediction_history[-4]
        if side == 'buy' and (predicted_price * trade_quantity) > fiat_balance:
            self.log.error('Buy order failed, insufficient funds.\nFiat Balance: {}\nPredicted Price: {}\nTrade Quantity: {}'.format(
                fiat_balance, predicted_price, trade_quantity))
            return None
        return Order.create(trade_quantity, side, TRADING_SYMBOL)
        # also check total account balance to determine portion

    def __execute_order(self, order: Order):
        '''
        If the last order in the list is the same as the current order, add the current order to the list.
        If the last order in the list is not the same as the current order, execute the last order and add
        the current order to the list

        :param order: The order that was just submitted
        :type order: Order
        '''
        if len(self.__orders) == 0:
            self.log.debug('No orders in list, adding new order')
            self.__orders.append(order)
            self.order_listener.submit_order(order)
        elif self.__orders[-1].side == order.side:
            self.log.debug('Same direction as last order, adding to list')
            self.__orders.append(order)
            self.order_listener.submit_order(order)
        elif self.__orders[-1].side != order.side:
            self.log('Opposite direction as last order, summing & inversing past orders')
            total_quantity = 0
            for order in self.__orders:
                total_quantity += order.quantity
            order.quantity += total_quantity
            self.order_listener.submit_order(order)
            self.__orders = []
        self.log.debug(
            f'Executed order: {order.side} {order.symbol} {order.quantity}')

    def __main_loop(self):
        '''
        Get the next prediction from the queue, get the current balances, and create an order based on the
        prediction, repeat until abort
        '''
        self.log.debug('Starting loop')
        try:
            while not self.abort:
                if self.__queue.qsize() > 0:
                    prediction: PredictionVector = self.__queue.get()
                    self.log.debug('Got prediction from queue')
                    balances = self.trading_account.get_trading_balance(
                        [CRYPTO_SYMBOL, FIAT_SYMBOL])
                    order = self.__create_order(prediction, balances)
                    if order:
                        self.__execute_order(order)
        except KeyboardInterrupt:
            self.abort()
        self.log.debug('Exiting loop')
