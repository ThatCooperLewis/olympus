import logging
import time
from utils import DiscordWebhook
from typing import List
from threading import Thread

class PrimordialChaos:

    def __init__(self):
        self.log: logging.Logger = None
        self.discord: DiscordWebhook = None
        self.abort: bool = False
        self.all_threads: List[Thread] = []

    def run(self):
        self.log.debug('Starting...')
        for thread in self.all_threads:
            thread.start()
    
    def join_threads(self):
        '''
        Wait for all active threads to finish
        '''
        self.stop()
        self.log.debug('Joining threads...')
        if not self.all_threads:
            self.log.warning('join_threads called without any threads. Did you forget to add them to all_threads?')
            return
        for thread in self.all_threads:
            if thread.is_alive():
                thread.join(timeout=10)

    def stop(self):
        '''
        Notify all active threads to end their loops (does not wait for them to finish)
        '''
        self.__check_log_status()
        self.log.debug('Aborting...')            
        self.abort = True

    def alert_with_error(self, error_message: str):
        self.__check_log_status()
        self.log.error(error_message)
        self.discord.send_alert(error_message)

    def __check_log_status(self):
        if type(self.log) is not logging.Logger or type(self.discord) is not DiscordWebhook:
            raise NotImplementedError('Logger or DiscordWebhook not set')
