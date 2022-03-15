from utils import Postgres, DiscordWebhook, Logger
from utils.config import TICKER_INTERVAL, STATUS_UPDATE_INTERVAL
from time import time as now
from time import sleep
import subprocess

class TickerMonitor:

    '''
    Ensures the ticker database is being continuously updated.
    '''

    def __init__(self) -> None:
        self.postgres = Postgres()
        self.discord = DiscordWebhook('TickerMonitor')
        self.log = Logger.setup("TickerMonitor")
        self.interval_threshhold = TICKER_INTERVAL * 2
        self.abort = False

    def run(self):
        hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        self.discord.send_status(f"TickerMonitor has started a new run. (Git hash: `{hash}`)")
        self.log.debug("TickerMonitor has started a new run.")

        last_good_count = self.postgres.get_ticker_count()
        last_good_time: int = now()
        
        self.start_time = now()
        self.latest_update = now()

        while not self.abort:
            try:
                try:
                    latest_count = self.postgres.get_ticker_count()
                except:
                    self.discord.send_alert("Postgres runtime error.")
                    self.log.error("Postgres runtime error.")
                    sleep(TICKER_INTERVAL)
                latest_time: int = now()

                if latest_count == last_good_count:
                    time_since_last_ticker = latest_time - last_good_time
                    # It's still the same
                    if time_since_last_ticker > self.interval_threshhold:
                        # If same for too long, raise alarms
                        self.discord.send_alert(
                            f"TickerScraper has been unresponsive for {time_since_last_ticker} seconds")
                        self.log.error(
                            f"TickerScraper has been unresponsive for {time_since_last_ticker} seconds")
                else:
                    # Ticker has changed, update last good
                    last_good_count = latest_count
                    last_good_time = latest_time
                
                if now() - self.latest_update > STATUS_UPDATE_INTERVAL:
                    try:
                        self.discord.send_status(
                            f"**TickerMonitor has been running for {(now() - self.start_time) / 60} minutes.**"
                            + f"\nTotal ticker count: {latest_count}"
                            + f"\nLatest ticker timestamp: {self.postgres.get_latest_tickers(1)[0].timestamp}"
                            + f"\nTickers stored in last hour: {self.postgres.get_ticker_count_for_last_hour()}"
                        )
                    except:
                        self.log.error("Failed to send status message to discord.")
                    self.latest_update = now()
                sleep(TICKER_INTERVAL/2)
            except KeyboardInterrupt:
                self.log.debug('KeyboardInterrupt')
                self.abort = True
            except:
                self.log.error("Unknown error.")
                sleep(TICKER_INTERVAL)

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
