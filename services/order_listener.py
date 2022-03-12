from time import sleep

import utils.config as constants
from olympus.hermes import Hermes
from olympus.primordial_chaos import PrimordialChaos
from utils import DiscordWebhook, Logger


class OrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.hermes = Hermes()
        self.abort = False

    def run(self):
        self.discord.send_alert("OrderListener has started a new run.")
        self.hermes.run()
        last_submission_count = self.hermes.status[1]
        # TODO: move this to monitor service
        try:
            while not self.abort:
                queue_size, submission_count = self.hermes.status
                if queue_size > constants.PREDICTION_QUEUE_MAX_SIZE and  last_submission_count == submission_count:
                    self.handle_timeout(self.hermes)
                    break
                else:
                    last_submission_count = submission_count
                sleep(5)
        except KeyboardInterrupt:
            self.abort = True
            self.hermes.stop()
            self.discord.send_alert("OrderListener has stopped (KeyboardInterrupt).")

    # TODO: Move to shared class.... maybe have this conform to Zeus?
    def handle_timeout(self, olympian: PrimordialChaos):
        if olympian.abort:
            self.log.debug(f'{olympian.__class__.__name__} has been aborted, ending loop')
        else:
            self.log.error(f'{olympian.__class__.__name__} has timed out, aborting Zeus...')
        return 

if __name__ == '__main__':
    OrderListener().run()