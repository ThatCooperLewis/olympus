from utils import Postgres, DiscordWebhook, Logger
from utils.config import TICKER_INTERVAL
from time import time as now 

class AthenaMonitor:

    def __init__(self) -> None:
        self.postgres = Postgres()
        self.discord = DiscordWebhook('AthenaMonitor')
        self.log = Logger.setup("AthenaMonitor")
        self.interval_multiplier_threshhold = 2

    def run(self):
        latest_timestamp = self.postgres.get_latest_tickers(1)[0].timestamp
        last_good_time = now()
        while True:
            current_timestamp = self.postgres.get_latest_tickers(1)[0]
            '''
            How to determine ticker hasn't updated in 2x the interval time
            two separate metrics: diff between latest timestamps & total time elapsed since last confimation

            '''
            if ((current_timestamp - latest_timestamp) > TICKER_INTERVAL*self.interval_multiplier_threshhold):
                self.discord.send_alert(f"Athena has not updated tickers to Postgres DB in {self.interval_multiplier_threshhold}X the typical interva ({TICKER_INTERVAL} seconds)")
            else:
                '''
                Gotta reset the most recent OK timer? Right?
                '''
                pass
if __name__ == "__main__":
    pass