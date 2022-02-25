from utils import Logger, DiscordWebhook
from olympus.hermes import Hermes

class HermesOrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.hermes = Hermes()

    # TODO: Use the run method from Zeus

    def run(self) -> None:
        self.discord.send_alert("HermesOrderListener has started a new run.")
        self.hermes.start()


if __name__ == '__main__':
    listener = HermesOrderListener()
    listener.run()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        listener.hermes.stop()
        listener.log.debug('KeyboardInterrupt')