import traceback
from threading import Thread
from typing import List, Tuple
from time import sleep

import utils.config as constants
from crosstower.models import Balance, Order
from crosstower.socket_api.private import OrderListener, Trading
from utils import DiscordWebhook, Logger, Postgres, GoogleSheets

from olympus.helper_objects import PredictionVector
from olympus.helper_objects.prediction_queue import \
    PredictionQueueDB as PredictionQueue
from olympus.primordial_chaos import PrimordialChaos

class Hermes(PrimordialChaos):

    '''
    Calculate order amounts based on predictions
    '''

    def __init__(self, override_orderListener: OrderListener = None, override_tradingAccount: Trading = None, override_predictionQueue: PredictionQueue = None) -> None:
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.gsheets = GoogleSheets()
        self.postgres = Postgres()
        self.abort = False
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
    def queue(self) -> PredictionQueue:
        return self.prediction_queue

    # Private

    def __parse_sell_quantity(self, prediction: PredictionVector, crypto_balance: float) -> float:
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
        return abs(percentage * crypto_balance)

    def __parse_buy_quantity(self, prediction: PredictionVector, usd_balance: float, current_btc_price: float) -> float:
        self.log.debug('Parsing buy quantity for prediction vector: {}'.format(prediction))
        percentage = constants.MAX_TRADE_PERCENTAGE * abs(prediction.weight)
        usd_buy_amount = percentage * usd_balance
        return abs(usd_buy_amount / current_btc_price)

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

    def __create_order(self, prediction: PredictionVector, current_btc_price: float, crypto_balance: float, fiat_balance: float) -> Order:
        if prediction.weight > 0:
            side = 'buy'
            trade_quantity: float = self.__parse_buy_quantity(prediction, fiat_balance, current_btc_price)
        elif prediction.weight < 0:
            side = 'sell'
            trade_quantity: float = self.__parse_sell_quantity(prediction, crypto_balance)
        else:
            self.log.debug('Prediction weight is 0, not executing order')
            return None
        self.log.debug(f'Quantity: {trade_quantity}')
        if side == 'buy' and (current_btc_price * trade_quantity) > fiat_balance:
            self.log.error('Buy order failed, insufficient funds.\nFiat Balance: {}\nPredicted Price: {}\nTrade Quantity: {}'.format(
                fiat_balance, current_btc_price, trade_quantity))
            return None
        if side == 'sell' and trade_quantity > crypto_balance:
            self.log.error('Sell order failed, insufficient funds.\nCrypto Balance: {}\nPredicted Price: {}\nTrade Quantity: {}'.format(
                crypto_balance, current_btc_price, trade_quantity))
            return None
        return Order.create(trade_quantity, side, constants.TRADING_SYMBOL, uuid=prediction.uuid)

    def __submit_order(self, order: Order, current_btc_price: float, crypto_balance: float, fiat_balance: float) -> None:
        """
        Submit order to the database.
        If the last order was in the opposite direction, sum the past orders 
        
        :param order: The order to submit
        :type order: Order
        """
        submitted = self.__order_status_processing
        completed = self.__order_status_complete
        new_order_side = order.side
        try:
            order_stack = self.postgres.get_latest_stack_of_same_orders()
        except IndexError:
            order_stack = []
        last_order_side = order_stack[0].side if len(order_stack) > 0 else None
        if last_order_side != new_order_side and len(order_stack) > 1:
            self.log.debug('Opposite direction as last order, summing & inversing past orders')
            past_quantity = 0
            # Skip the first order, which was the last summed order
            # Inverse the rest of the orders
            orders_to_sum = order_stack[1:11]
            for past_order in orders_to_sum:
                past_quantity += abs(past_order.quantity)
            order.quantity += past_quantity
        self.postgres.insert_order(order, current_btc_price, crypto_balance, fiat_balance)
        self.order_listener.submit_order(order, submitted, completed)
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
                    balances = self.trading_account.get_trading_balance([constants.CRYPTO_SYMBOL, constants.FIAT_SYMBOL])
                    crypto_balance, fiat_balance = self.__parse_balances(balances)
                    current_btc_price = self.postgres.get_latest_tickers(1)[0].ask
                    self.log.debug('Got balances and current price')
                    order = self.__create_order(prediction, current_btc_price, crypto_balance, fiat_balance)
                    if order:
                        self.__submit_order(order, current_btc_price, crypto_balance, fiat_balance)
                    self.prediction_queue.close(prediction, failed=(order is None))
                    sleep(1)
                    try:
                        self.gsheets.update_order_feed()
                    except:
                        self.log.error("Could not rotate order feed. Prob expired token?")
                sleep(0.2)
        except KeyboardInterrupt:
            self.log.debug('Keyboard interrupt received, aborting')
            self.abort = True
        except Exception:
            self.alert_with_error('Error in main loop', traceback.format_exc())
            self.stop()
        self.log.debug('Exiting loop')
