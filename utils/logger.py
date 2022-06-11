import logging
from logging.handlers import RotatingFileHandler
from utils.config import General as config
import subprocess

class Logger():
    '''
    Make logging simple.
    Call `Logger.setup('example.name')` to get a formatted logger.
    '''
        
    @classmethod
    def setup(cls, category_str: str):
        '''
        Create a `logging` object with a given name, and attach a formatter to it
        
        :param category_str: The name of the logger
        :type category_str: str
        :return: A logger object.
        '''
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            if logger.name == category_str:
                return logger
        logger = logging.getLogger(category_str)
        

        # Setup CLI logging stream
        console = logging.StreamHandler()
        console_format = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        console.setFormatter(console_format)
        console.setLevel(config.STREAM_LOGGING_LEVEL)
        logger.addHandler(console)

        # Setup file logging
        file_format = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        file_handler = RotatingFileHandler(config.LOGGING_FILENAME, mode='a', maxBytes=5*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
        file_handler.setFormatter(file_format)
        file_handler.setLevel(config.FILE_LOGGING_LEVEL)
        logger.addHandler(file_handler)
        logger.level = config.FILE_LOGGING_LEVEL

        return logger
    
    @classmethod
    def git_hash(cls):
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()