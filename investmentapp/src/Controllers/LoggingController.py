#!/venv/bin/python

# external dependencies 
import os
import logging
import time
import inspect
import sys


def initLogging():
    """
    initLogging initialises the logging object to be used throughout the program, providing a logging file, format and date format
    :testedWith: None - library config code
    :return: the configured logging object
    """
    logFormat = '%(asctime)s - %(levelname)s - %(message)s'
    programName = "etfbot"
    logDateFormat = '%d-%b-%y %H:%M:%S'
    programName += f"-{inspect.getframeinfo(sys._getframe(1)).filename.split('/')[-1].replace('.py', '')}"
    projectBaseDir = os.getenv("LOGS_DIR") if os.getenv("LOGS_DIR") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")

    if os.getenv("ENVIRONMENT") == "production":
        logFilename = os.path.join(projectBaseDir, f"{programName}_{time.strftime('%d-%m-%Y_%H-%M')}.log")
        logging.basicConfig(filename=logFilename, filemode='w', format=logFormat, datefmt=logDateFormat, level=logging.INFO)
    else:
        logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=logging.DEBUG)


    logging.info(f"Logging initialised, mode: {os.getenv('ENVIRONMENT')}")

    return logging
