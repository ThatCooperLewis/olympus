import subprocess
from time import sleep
from time import time as now
from typing import List

from crosstower.models import Order
from olympus.helper_objects.prediction_vector import PredictionVector
from utils import DiscordWebhook, Logger, Postgres, config
from utils.config import PostgresConfig, ScraperConfig, PredictionConfig


class PostgresSubservice:

    '''
    Mini class used to differentiate discord alerts and inactivity monitoring for each service
    '''

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
        self.ticker_scraper_subservice = PostgresSubservice('TickerScraper')
        self.order_listener_subservice = PostgresSubservice('OrderListener')
        self.prediction_engine_subservice = PostgresSubservice('PredictionEngine')
        self.abort = False

    # Public methods

    def run(self):
        hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        self.discord.send_status(f"PostgresMonitor has started a new run (Git hash: `{hash}`)")
        self.log.debug("PostgresMonitor has started a new run.")
        right_now = now()

        self.last_good_ticker_count: int = self.postgres.get_ticker_count()
        self.last_good_ticker_time: int = right_now
        
        queued_orders = self.postgres.get_queued_orders()
        self.last_good_queued_order: Order = queued_orders[-1] if queued_orders else None
        self.last_good_queued_order_time: int = right_now

        queued_predictions = self.postgres.get_queued_predictions()
        self.last_good_queued_prediction: PredictionVector = queued_predictions[-1] if queued_predictions else None
        self.last_good_queued_prediction_time: int = right_now

        self.start_time = right_now
        self.latest_update = right_now

        # Sleep a little, prevent false positives
        sleep(ScraperConfig.TICKER_INTERVAL/2)

        while not self.abort:
            try:
                self.__ticker_check()
                self.__order_check()
                self.__prediction_check()
                self.__status_update()
                sleep(ScraperConfig.TICKER_INTERVAL/2)
            except KeyboardInterrupt:
                self.log.debug('KeyboardInterrupt')
                self.abort = True
            except Exception as e:
                self.log.error(f"Unknown error: {e}")
                self.discord.send_alert(f"Unknown error: {e}")
                sleep(ScraperConfig.TICKER_INTERVAL)

    def stop(self):
        self.abort = True

    # Monitoring methods

    def __ticker_check(self):
        latest_count = self.postgres.get_ticker_count()
        latest_time: int = now()

        if latest_count == self.last_good_ticker_count:
            self.ticker_scraper_subservice = self.__handle_timeout_and_update_subservice(
                subservice=self.ticker_scraper_subservice, 
                time_since_last_update=int(latest_time - self.last_good_ticker_time),
                unresponsive_threshold=int(ScraperConfig.TICKER_INTERVAL*2),
                abandon_threshold=int(PostgresConfig.UNRESPONSIVE_TIMEOUT_THRESHOLD)
            )
        else:
            self.last_good_ticker_count = latest_count
            self.last_good_ticker_time = latest_time
            self.ticker_scraper_subservice = self.__handle_service_revival_if_inactive(self.ticker_scraper_subservice)
            
    def __order_check(self):
        queued_orders = self.postgres.get_queued_orders()
        if not queued_orders:
            self.log.debug("No queued orders, continuing..")
            return
        
        latest_queued_order = queued_orders[-1]
        latest_time = now()
        if latest_queued_order.uuid == self.last_good_queued_order.uuid:
            self.order_listener_subservice = self.__handle_timeout_and_update_subservice(
                subservice=self.order_listener_subservice, 
                time_since_last_update=int(latest_time - self.last_good_queued_order_time),
                unresponsive_threshold=int(ScraperConfig.TICKER_INTERVAL*2),
                abandon_threshold=int(PostgresConfig.UNRESPONSIVE_TIMEOUT_THRESHOLD)
            )
        else:
            self.last_good_queued_order = latest_queued_order
            self.last_good_queued_order_time = latest_time
            self.order_listener_subservice = self.__handle_service_revival_if_inactive(self.order_listener_subservice)

    def __prediction_check(self):
        try:
            queued_predictions = self.postgres.get_queued_predictions()
        except IndexError:
            self.log.debug("No queued predictions, continuing..")
            return
        if not queued_predictions:
            self.log.debug("No queued predictions, continuing..")
            return
        
        latest_queued_prediction = queued_predictions[-1]
        latest_time = now()
        prediction_gap = ScraperConfig.TICKER_INTERVAL*PredictionConfig.PREDICTION_ITERATION_COUNT

        if latest_queued_prediction.uuid == self.last_good_queued_prediction.uuid:
            self.prediction_engine_subservice = self.__handle_timeout_and_update_subservice(
                subservice=self.prediction_engine_subservice, 
                time_since_last_update=int(latest_time - self.last_good_queued_prediction_time),
                unresponsive_threshold=int(prediction_gap*2),
                abandon_threshold=int(prediction_gap*4)
            )
        else:
            self.last_good_queued_prediction = latest_queued_prediction
            self.last_good_queued_prediction_time = latest_time
            self.prediction_engine_subservice = self.__handle_service_revival_if_inactive(self.prediction_engine_subservice)

    # Helper methods

    def __status_update(self):
        if now() - self.latest_update > config.General.STATUS_UPDATE_INTERVAL:
            try:
                self.discord.send_status(
                    f"**PostgresMonitor has been running for {int((now() - self.start_time) / 60)} minutes.**"
                    + f"\nTotal ticker count: {self.postgres.get_ticker_count()}"
                    + f"\nLatest ticker timestamp: {self.postgres.get_latest_tickers(1)[0].timestamp}"
                    + f"\nTickers stored in last hour: {self.postgres.get_ticker_count_for_last_hour()}"
                )
            except:
                self.log.error("Failed to send status message to discord.")
            self.latest_update = now()

    def __handle_timeout_and_update_subservice(self, subservice: PostgresSubservice, time_since_last_update: int, unresponsive_threshold: int, abandon_threshold: int) -> PostgresSubservice:
        if time_since_last_update > unresponsive_threshold and not subservice.ignore_inactivity:
            if time_since_last_update > abandon_threshold:
                msg = f"{subservice.name} has exceeded the unresponsive timeout threshold. Assume it has completely shut down unless another update appears."
                subservice.ignore_inactivity = True
            else:
                msg = f"{subservice.name} has been unresponsive for {time_since_last_update} seconds"
            self.discord.send_alert(msg)
            self.log.error(msg)
        return subservice

    def __handle_service_revival_if_inactive(self, subservice: PostgresSubservice) -> PostgresSubservice:
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
