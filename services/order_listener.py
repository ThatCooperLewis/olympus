from olympus.hermes import Hermes
from utils import DiscordWebhook, Logger

class OrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.hermes = Hermes()
        self.abort = False

    def run(self):
        self.discord.send_status(f"OrderListener has started a new run. (Git hash: `{Logger.git_hash()}`)")
        self.hermes.run()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.hermes.stop()
            self.log.debug('KeyboardInterrupt')

if __name__ == '__main__':
    OrderListener().run()