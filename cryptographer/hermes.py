import queue
from queue import Queue
from threading import Condition, Thread
from time import time as now

from crosstower import config
from crosstower.models import Order
from crosstower.socket_api.private import OrderListener

'''

- should we hodl when it drops? sell on the way down?
- change amount based on confidence level (including inverse maybe?)
- Include regular check for failed orders

'''


class ConfidenceTicker:

    # Simple solution for useful queue objects
    def __init__(self, weight, predictions, timestamp):
        self.weight = weight
        self.prediction_history = predictions
        self.timestamp = timestamp


class Hermes:

    def __init__(self) -> None:
        self.__queue: Queue = Queue()
        self.__thread: Thread = Thread(target=self.__main_loop, args=())
        self.__order_listener = OrderListener()
        self.__last_order = (Order, ConfidenceTicker)

    # Public

    def submit(self, queue_object: ConfidenceTicker):
        '''
        Submit a new ConfidenceTicker to the queue, starting a new order process
        '''
        if type(queue_object) is not ConfidenceTicker:
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

    def __create_order(confidence: ConfidenceTicker) -> Order:
        # parse confidence object
        # determine buy/sell and how much
        # also check total account balance to determine portion
        pass

    def __create_follower_order(last_order: Order, new_confidence: ConfidenceTicker) -> Order:
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
                    confidence: ConfidenceTicker = self.__queue.get()
                    if self.__last_order:
                        last_order = self.__last_order
                        follower_order = self.__create_follower_order(last_order, confidence)
                        if follower_order:
                            self.__order_listener.submit_order(follower_order)
                    order = self.__create_order(confidence)
                    self.__order_listener.submit_order(order)
                    self.__last_order = order 
        except KeyboardInterrupt:
            self.abort()
