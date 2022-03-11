from utils import Postgres, DiscordWebhook, Logger
from utils.config import TICKER_INTERVAL, STATUS_UPDATE_INTERVAL
from time import time as now
from time import sleep


class TickerMonitor:

    '''
    Ensures the ticker database is being continuously updated.
    '''

    def __init__(self) -> None:
        self.postgres = Postgres()
        self.discord = DiscordWebhook('TickerMonitor')
        self.log = Logger.setup("TickerMonitor")
        self.interval_multiplier_threshhold = 2
        self.abort = False

    def run(self):
        self.discord.send_status("TickerMonitor has started a new run.")
        self.log.debug("TickerMonitor has started a new run.")
        last_good_ticker = self.postgres.get_latest_tickers(1)[0]
        last_good_time: int = now()
        
        self.start_time = now()
        self.latest_update = now()

        while not self.abort:
            latest_ticker = self.postgres.get_latest_tickers(1)[0]
            latest_time: int = now()

            if latest_ticker.timestamp == last_good_ticker:
                if (latest_time - last_good_time) > TICKER_INTERVAL*self.interval_multiplier_threshhold:
                    self.discord.send_alert(
                        f"TickerScraper has been unresponsive for {latest_ticker.timestamp - last_good_time} seconds")
                    self.log.error(
                        f"TickerScraper has been unresponsive for {latest_ticker.timestamp - last_good_time} seconds")
            else:
                last_good_ticker = latest_ticker
                last_good_time = latest_ticker.timestamp
            
            if now() - self.latest_update > STATUS_UPDATE_INTERVAL:
                try:
                    self.discord.send_status(
                        f"**TickerMonitor has been running for {(now() - self.start_time) / 60} minutes.**"
                        + f"\nLatest ticker timestamp: {latest_ticker.timestamp}"
                        + f"\nTickets stored in last hour: {self.postgres.get_ticker_count_for_last_hour()}"
                    )
                except:
                    self.log.error("Failed to send status message to discord.")
                self.latest_update = now()
            sleep(TICKER_INTERVAL/2)

    def stop(self):
        self.abort = True


if __name__ == "__main__":
    try:
        monitor = TickerMonitor()
        monitor.run()
    except KeyboardInterrupt:
        monitor.stop()
        monitor.log.debug('KeyboardInterrupt')
    except Exception as e:
        discord = DiscordWebhook('TickerMonitor')
        discord.send_alert(f"Something has gone horribly wrong: {e}")
