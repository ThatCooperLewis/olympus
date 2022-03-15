from time import sleep
import utils.config as constants
from olympus.hermes import Hermes
from olympus.primordial_chaos import PrimordialChaos
from utils import DiscordWebhook, Logger
import subprocess

class OrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.hermes = Hermes()
        self.abort = False

    def run(self):
        hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
        self.discord.send_alert(f"OrderListener has started a new run. (Git hash: `{hash}`)")
        self.hermes.run()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.hermes.stop()
            self.log.debug('KeyboardInterrupt')

if __name__ == '__main__':
    OrderListener().run()