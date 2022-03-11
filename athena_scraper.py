from utils import Logger, DiscordWebhook
from olympus.athena import Athena

class TickerScraper:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.athena = Athena(custom_interval=60)

    # TODO: Use the run method from Zeus

    def run(self) -> None:
        self.discord.send_alert("TickerScraper has started a new run.")
        self.athena.run(headless=True)

if __name__ == '__main__':
    scraper = TickerScraper()
    scraper.run()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scraper.athena.stop()
        scraper.log.debug('KeyboardInterrupt')
