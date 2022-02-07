import imp
import logging
from utils.logger import Logger


class Logger():

    # Make the logging process a little more streamlined/less verbose

    def __init__(self, category_str):
        logging.basicConfig()
        self.log = logging.getLogger()
        self.category = category_str
        self.log.setLevel(logging.INFO)

    def info(self, message):
        self.log.info('{0}: {1}'.format(self.category, message))

    def warn(self, message):
        self.log.warning('{0}: {1}'.format(self.category, message))

    def error(self, message):
        self.log.error('{0}: {1}'.format(self.category, message))

    def debug(self, message):
        self.log.debug('{0}: {1}'.format(self.category, message))