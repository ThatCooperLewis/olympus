from utils import Logger, DiscordWebhook
from olympus.athena import Athena
from time import sleep


class TickerScraper:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.athena = Athena(custom_interval=60)

    def run(self) -> None:
        self.discord.send_status(f"TickerScraper has started a new run (Git hash: `{Logger.git_hash()}`)")
        self.athena.run(headless=True)
        try:
            while not self.athena.abort:
                sleep(10)
        except KeyboardInterrupt:
            self.athena.stop()
            self.log.debug('KeyboardInterrupt')

if __name__ == '__main__':
    scraper = TickerScraper()
    scraper.run()
