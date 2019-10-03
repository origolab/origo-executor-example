import logging

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)


class LogUtils:
    """
    The util class for logging.
    """
    @staticmethod
    def info(log_msg):
        logging.critical(log_msg)

    @staticmethod
    def error(error_msg):
        logging.error(error_msg)

    @staticmethod
    def warning(warning_msg):
        logging.warning(warning_msg)
