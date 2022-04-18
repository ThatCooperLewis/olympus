from re import sub
import subprocess
from time import sleep
from time import time as now
from typing import List
from utils import DiscordWebhook, Logger, Postgres
from crosstower.models import Order, Ticker
from utils.config import (PREDICTION_QUEUE_MAX_SIZE, STATUS_UPDATE_INTERVAL,
                          TICKER_INTERVAL, UNRESPONSIVE_TIMEOUT_THRESHOLD)

class PostgresSubservice:

    def __init__(self, name: str) -> None:
        self.ignore_inactivity = False
        self.name = name


class PostgresMonitor:

    '''
    Ensures the ticker database is being continuously updated.
    '''

    def __init__(self) -> None:
        self.postgres = Postgres()
        self.discord = DiscordWebhook('PostgresMonitor')
        self.log = Logger.setup("PostgresMonitor")
        self.interval_threshhold = TICKER_INTERVAL * 2
        self.ticker_scraper = PostgresSubservice('TickerScraper')
        self.order_listener = PostgresSubservice('OrderListener')
        self.abort = False

    def run(self):
        hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        self.discord.send_status(f"PostgresMonitor has started a new run. (Git hash: `{hash}`)")
        self.log.debug("PostgresMonitor has started a new run.")

        self.last_good_ticker_count: List[Ticker] = self.postgres.get_ticker_count()
        self.last_good_ticker_time: int = now()
        
        queued_orders = self.postgres.get_queued_orders()
        self.last_good_queued_order: Order = queued_orders[-1] if queued_orders else None
        self.last_good_queued_order_time: int = now()

        self.start_time = now()
        self.latest_update = now()

        while not self.abort:
            try:
                self.__ticker_check()
                self.__order_check()
                self.__status_update()
                sleep(TICKER_INTERVAL/2)
            except KeyboardInterrupt:
                self.log.debug('KeyboardInterrupt')
                self.abort = True
            except Exception as e:
                self.log.error(f"Unknown error: {e}")
                sleep(TICKER_INTERVAL)

    def stop(self):
        self.abort = True

    def __ticker_check(self):
        try:
            latest_count = self.postgres.get_ticker_count()
        except:
            self.discord.send_alert("Postgres runtime error.")
            self.log.error("Postgres runtime error.")
            sleep(TICKER_INTERVAL)
        latest_time: int = now()

        if latest_count == self.last_good_ticker_count:
            self.ticker_scraper = self.__handle_timeout_and_update_subservice(self.ticker_scraper, int(latest_time - self.last_good_ticker_time))
        else:
            self.last_good_ticker_count = latest_count
            self.last_good_ticker_time = latest_time
            self.ticker_scraper = self.__handle_service_revival(self.ticker_scraper)
            
    def __order_check(self):
        queued_orders = self.postgres.get_queued_orders()
        if not queued_orders:
            self.log.debug("No queued orders, continuing..")
            return
        latest_queued_order = queued_orders[-1]
        latest_time = now()
        if latest_queued_order.uuid == self.last_good_queued_order.uuid:
            self.order_listener = self.__handle_timeout_and_update_subservice(self.order_listener, int(latest_time - self.last_good_queued_order_time))
        else:
            self.last_good_queued_order = latest_queued_order
            self.last_good_queued_order_time = latest_time
            self.order_listener = self.__handle_service_revival(self.order_listener)

    def __status_update(self):
        if now() - self.latest_update > STATUS_UPDATE_INTERVAL:
            try:
                self.discord.send_status(
                    f"**PostgresMonitor has been running for {int((now() - self.start_time) / 60)} minutes.**"
                    # TODO: Order status
                    + f"\nTotal ticker count: {self.postgres.get_ticker_count()}"
                    + f"\nLatest ticker timestamp: {self.postgres.get_latest_tickers(1)[0].timestamp}"
                    + f"\nTickers stored in last hour: {self.postgres.get_ticker_count_for_last_hour()}"
                )
            except:
                self.log.error("Failed to send status message to discord.")
            self.latest_update = now()

    def __handle_timeout_and_update_subservice(self, subservice: PostgresSubservice, time_since_last_update: int) -> PostgresSubservice:
        if time_since_last_update > self.interval_threshhold and not subservice.ignore_inactivity:
            if time_since_last_update > UNRESPONSIVE_TIMEOUT_THRESHOLD:
                msg = f"{subservice.name} has exceeded the unresponsive timeout threshold. Assume it has completely shut down unless another update appears."
                subservice.ignore_inactivity = True
            else:
                msg = f"{subservice.name} has been unresponsive for {time_since_last_update} seconds"
            self.discord.send_alert(msg)
            self.log.error(msg)
        return subservice

    def __handle_service_revival(self, subservice: PostgresSubservice) -> PostgresSubservice:
        if subservice.ignore_inactivity:
            msg = f'{subservice.name} was previsouly unresponsive, but has started updating again. Resuming monitoring...'
            self.discord.send_alert(msg)
            self.log.info(msg)
            subservice.ignore_inactivity = False
        return subservice

if __name__ == "__main__":
    try:
        monitor = PostgresMonitor()
        monitor.run()
    except KeyboardInterrupt:
        monitor.stop()
        monitor.log.debug('KeyboardInterrupt')
    except Exception as e:
        discord = DiscordWebhook('PostgresMonitor')
        discord.send_alert(f"Something has gone horribly wrong: {e}")
