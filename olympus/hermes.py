import traceback
from threading import Thread
from typing import List, Tuple
from time import sleep

import utils.config as constants
from crosstower.models import Balance, Order
from crosstower.socket_api.private import OrderListener, Trading
from utils import DiscordWebhook, Logger, Postgres

from olympus.helper_objects import PredictionVector
from olympus.helper_objects.prediction_queue import \
    PredictionQueueDB as PredictionQueue
from olympus.primordial_chaos import PrimordialChaos

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

class Hermes(PrimordialChaos):

    '''
    Calculate order amounts based on predictions
    '''

    def __init__(self, override_orderListener: OrderListener = None, override_tradingAccount: Trading = None, override_predictionQueue: PredictionQueue = None) -> None:
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.postgres = Postgres()
        self.abort = False
        self.__orders: List[Order] = []
        self.__main_thread: Thread = Thread(target=self.__main_loop, args=())
        self.submitted_order_count = 0 # Used for tracking activity status
        
        self.order_listener: OrderListener = override_orderListener if override_orderListener is not None else OrderListener()
        self.trading_account: Trading = override_tradingAccount if override_tradingAccount else Trading()
        self.prediction_queue: PredictionQueue = override_predictionQueue if override_predictionQueue else PredictionQueue(self.postgres)
        
        # Order listener is not itself a thread, but is a wrapper for a thread
        self.all_threads = [self.order_listener, self.__main_thread]

    # Public

    def stop(self):
        # Reverse thread list so they shut down in the right order
        self.all_threads.reverse()
        super().stop()
        self.all_threads.reverse()

    def submit_prediction_to_queue(self, queue_object: PredictionVector):
        '''
        Submit a new PredictionVector to the queue, starting a new order process
        '''
        self.prediction_queue.put(queue_object)
    
    @property
    def status(self) -> Tuple[int, int]:
        '''
        Returns the size of the prediction queue, and the total number of orders submitted. 
        '''
        return self.prediction_queue.size, self.submitted_order_count

    @property
    def queue(self) -> PredictionQueue:
        return self.prediction_queue

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
        percentage = constants.MAX_TRADE_PERCENTAGE * abs(prediction.weight)
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
            if balance.currency == constants.FIAT_SYMBOL:
                fiat_balance = balance.available
            elif balance.currency == constants.CRYPTO_SYMBOL:
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
        return Order.create(trade_quantity, side, constants.TRADING_SYMBOL, uuid=prediction.uuid)
        # also check total account balance to determine portion

    def __submit_order(self, order: Order):
        '''
        If the last order in the list is the same as the current order, add the current order to the list.
        If the last order in the list is not the same as the current order, execute the last order and add
        the current order to the list

        :param order: The order that was just submitted
        :type order: Order
        '''
        submitted = self.__order_status_processing
        completed = self.__order_status_complete
        new_order_side = order.side
        last_order_side = self.__orders[-1].side if len(self.__orders) > 0 else None
        if len(self.__orders) == 0:
            self.log.debug('No orders in list, adding new order')
            self.__orders.append(order)
            self.order_listener.submit_order(order, submitted, completed)
        elif last_order_side == new_order_side:
            self.log.debug('Same direction as last order, adding to list')
            self.__orders.append(order)
            self.order_listener.submit_order(order, submitted, completed)
        elif last_order_side != new_order_side:
            self.log.debug('Opposite direction as last order, summing & inversing past orders')
            total_quantity = 0
            for order in self.__orders:
                total_quantity += order.quantity
            order.quantity += total_quantity
            self.order_listener.submit_order(order, submitted, completed)
            self.__orders = []
        self.log.debug(f'Executed order: {order.side} {order.symbol} {order.quantity}')
        self.submitted_order_count += 1

    def __order_status_processing(self, order: Order):
        self.postgres.update_order_status(order.uuid, constants.POSTGRES_STATUS_PROCESSING)
        
    def __order_status_complete(self, order: Order):
        self.postgres.update_order_status(order.uuid, constants.POSTGRES_STATUS_COMPLETE)

    def __main_loop(self):
        '''
        Get the next prediction from the queue, get the current balances, and create an order based on the
        prediction, repeat until abort
        '''
        self.log.debug('Starting loop')
        try:
            while not self.abort:
                if self.prediction_queue.size > 0:
                    prediction = self.prediction_queue.get()
                    self.log.debug('Got prediction from queue')
                    balances = self.trading_account.get_trading_balance(
                        [constants.CRYPTO_SYMBOL, constants.FIAT_SYMBOL])
                    order = self.__create_order(prediction, balances)
                    if order:
                        self.__submit_order(order)
                    self.prediction_queue.close(prediction, failed=(order is None))
                sleep(0.2)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received, aborting')
            self.abort = True
        except Exception:
            self.alert_with_error('Error in main loop', traceback.format_exc())
            self.stop()
        self.log.debug('Exiting loop')
