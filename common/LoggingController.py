#!/venv/bin/python

# external dependencies 
import os
import logging
import time
import datetime
import re


def getLogsDir():
    return os.getenv("LOGS_DIR") if os.getenv("LOGS_DIR") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")


def initLogging(forceStdoutLogging=False):
    """
    initLogging initialises the logging object to be used throughout the program, providing a logging file, format and date format
    :testedWith: None - library config code
    :return: the configured logging object
    """
    logFormat = '%(asctime)s - %(levelname)s - %(message)s'
    programName = "etfbot"
    logDateFormat = '%d-%b-%y %H:%M:%S'
    projectBaseDir = getLogsDir()

    if os.getenv("ENVIRONMENT") == "production" and not forceStdoutLogging:
        logFilename = os.path.join(projectBaseDir, f"{programName}_{time.strftime('%d-%m-%Y_%H-%M')}.log")
        logging.basicConfig(filename=logFilename, filemode='w', format=logFormat, datefmt=logDateFormat, level=logging.INFO)
    else:
        logging.basicConfig(format=logFormat, datefmt=logDateFormat, level=logging.INFO)

    logging.info(f"Logging initialised, mode={os.getenv('ENVIRONMENT')} forceStdoutLogging={forceStdoutLogging}")

    return logging


def listExistingLogFiles():
    logsDir = getLogsDir()
    logFiles = [f for f in os.listdir(logsDir) if os.path.isfile(os.path.join(logsDir, f))]

    # sort log files by date
    def sortLogFileNames(logFileName):
        # e.g. log file name: etfbot_22-08-2024_18-45.log
        regexPattern = r"etfbot.*_(\d{2})-(\d{2})-(\d{4})_(\d{2})-(\d{2})\.log"
        result = re.search(regexPattern, logFileName)
        if result:
            return datetime.datetime(
                int(result.group(3)),
                int(result.group(2)),
                int(result.group(1)),
                int(result.group(4)),
                int(result.group(5))
            ).timestamp()

    return sorted(logFiles, key=sortLogFileNames, reverse=True)

def getLatestLogContent():
    latestLogFilePath = listExistingLogFiles()[0]
    with open(os.path.join(getLogsDir(), latestLogFilePath),'r') as latestLogFile:
        return latestLogFile.read()