#!/venv/bin/python

# external dependencies 
import os
import logging
import time


def initLogging():
    """
    initLogging initialises the logging object to be used throughout the program, providing a logging file, format and date format
    :testedWith: None - library config code
    :return: the configured logging object
    """
    logFormat = '%(asctime)s - %(levelname)s - %(message)s'
    logDateFormat = '%d-%b-%y %H:%M:%S'
    projectBaseDir = os.getenv("LOGS_DIR") if os.getenv("LOGS_DIR") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

    if os.getenv("ENVIRONMENT") == "production":
        logFilename = os.path.join(projectBaseDir, f"media-grab_{time.strftime('%d-%m-%Y_%H-%M')}.log")
        logging.basicConfig(filename=logFilename, filemode='w', format=logFormat, datefmt=logDateFormat, level=logging.INFO)
    else:
        logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=logging.INFO)

    logging.debug('Logging initialised.')
    return logging
