import logging

from colorlog import ColoredFormatter


def setup_custom_logger(name):
    """
    Setup a custom logger with colored outputs for different log levels.
    """
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)-8s - %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


# This will create a logger to be used throughout the module
logger = setup_custom_logger('app_logger')
