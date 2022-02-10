import logging


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
        logger = logging.getLogger(category_str)
        console = logging.StreamHandler()
        console_format = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        console.setFormatter(console_format)
        logger.addHandler(console)
        return logger
