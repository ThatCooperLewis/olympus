from utils import Logger
from olympus import Athena

class AthenaScraper:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.athena = Athena(custom_interval=5)

    def run(self) -> None:
        self.athena.run(headless=True)

if __name__ == '__main__':
    scraper = AthenaScraper()
    scraper.run()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scraper.athena.stop()
        scraper.log.debug('KeyboardInterrupt')
