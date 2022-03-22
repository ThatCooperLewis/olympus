import subprocess
from time import sleep
from time import time as now
from typing import List
from utils import DiscordWebhook, Logger, Postgres
from crosstower.models import Order, Ticker
from utils.config import (PREDICTION_QUEUE_MAX_SIZE, STATUS_UPDATE_INTERVAL,
                          TICKER_INTERVAL)


class PostgresMonitor:

    '''
    Ensures the ticker database is being continuously updated.
    '''

    def __init__(self) -> None:
        self.postgres = Postgres()
        self.discord = DiscordWebhook('PostgresMonitor')
        self.log = Logger.setup("PostgresMonitor")
        self.interval_threshhold = TICKER_INTERVAL * 2
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
            time_since_last_ticker = latest_time - self.last_good_ticker_time
            # It's still the same
            if time_since_last_ticker > self.interval_threshhold:
                # If same for too long, raise alarms
                self.discord.send_alert(
                    f"TickerScraper has been unresponsive for {int(time_since_last_ticker)} seconds")
                self.log.error(
                    f"TickerScraper has been unresponsive for {int(time_since_last_ticker)} seconds")
        else:
            # Ticker has changed, update last good
            self.last_good_ticker_count = latest_count
            self.last_good_ticker_time = latest_time
            
    def __order_check(self):
        queued_orders = self.postgres.get_queued_orders()
        if not queued_orders:
            self.log.debug("No queued orders, continuing..")
            return
        latest_queued_order = queued_orders[-1]
        latest_time = now()
        if latest_queued_order.uuid == self.last_good_queued_order.uuid:
            time_since_last_order = latest_time - self.last_good_queued_order_time
            if time_since_last_order > self.interval_threshhold:
                self.discord.send_alert(
                    f"OrderListener has been unresponsive for {int(time_since_last_order)} seconds.")
                self.log.error(
                    f"OrderListener has been unresponsive for {int(time_since_last_order)} seconds.")
        else:
            self.last_good_queued_order = latest_queued_order
            self.last_good_queued_order_time = latest_time

    def __status_update(self):
        if now() - self.latest_update > STATUS_UPDATE_INTERVAL:
            try:
                self.discord.send_status(
                    f"**PostgresMonitor has been running for {(now() - self.start_time) / 60} minutes.**"
                    # TODO: Order status
                    + f"\nTotal ticker count: {self.postgres.get_ticker_count()}"
                    + f"\nLatest ticker timestamp: {self.postgres.get_latest_tickers(1)[0].timestamp}"
                    + f"\nTickers stored in last hour: {self.postgres.get_ticker_count_for_last_hour()}"
                )
            except:
                self.log.error("Failed to send status message to discord.")
            self.latest_update = now()

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
