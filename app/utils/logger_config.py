"""
This module provides a utility function to set up a colored logger using the colorlog library.

Functions:
    setup_logger(logger_name=None): Sets up and returns a logger with colored output.
"""

import logging
from colorlog import ColoredFormatter


def setup_logger(logger_name=None):
    """
    Sets up and returns a logger with colored output using the colorlog library.

    Args:
        logger_name (str, optional): Name of the logger. Defaults to the name of the calling module.

    Returns:
        logging.Logger: Configured logger with colored output.
    """
    logger_name = logger_name or __name__

    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the log level to DEBUG to capture all the logs
    logger.setLevel(logging.INFO)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Define log colors
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }

    # Define the log format
    log_format = "%(log_color)s[%(levelname)s] %(asctime)s - %(message)s%(reset)s"

    # Create a formatter
    formatter = ColoredFormatter(log_format, log_colors=log_colors)

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(console_handler)

    return logger
