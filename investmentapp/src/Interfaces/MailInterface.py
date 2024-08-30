#!/venv/bin/python

# external dependencies
import smtplib
import os
import logging
from email.message import EmailMessage
import sys
import datetime

sys.path.append("..") # makes investmentapp accessible (during app run)

# internal dependencies
if __name__== "__main__": # horrible but just for testing
    sys.path.append("/home/tom/projects/etfbot")# makes investmentapp accessible (during file run)
from webapp.server.controllers.LoggingController import getLatestLogContent

class MailInterface():

    def __init__(self, fromEmailAddress=None, toEmailAddress=None, environment=None):
        """
        __init__ initialises all private members of the object
        :testedWith: None - tested indirectly
        :param enterLogMessage: optional log message to print upon entry to the sendMail message, the param is to allow overwriting for amongst other purposes, testing.
        :param fromEmailAddress: optional notification from address, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param toEmailAddress: optional notification target email address, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        :param environment: optional dev/production mode for the program run, the param is to allow overwriting for amongst other purposes, testing, if not provided the value will be drawn from the .env file.
        """
        # assign class properties if they are provided, use defaults if they are not
        self._fromEmailAddress = fromEmailAddress if fromEmailAddress else os.getenv("NOTIFICATION_FROM_ADDRESS")
        self._toEmailAddress = toEmailAddress if toEmailAddress else os.getenv("NOTIFICATION_TO_ADDRESS")
        self._environment = environment if environment else os.getenv("ENVIRONMENT")



    ##### Public functions start #####

    def sendInvestmentAppSummaryMail(self, success):

        successHeading = "Investment app run successfully"
        failureHeading = "Investment app run failed"

        mailHeading = successHeading if success else failureHeading
        
        # get most recent log file content
        logContent = str(getLatestLogContent())

        self._sendMail(mailHeading, logContent)

    ##### Public functions end #####


    ##### Private functions start #####

    def _sendMail(self, heading, messageBody):
        """
        __sendMail sends an email containing a notification
        :testedWith: TestMailInterface:test_sendMailSingleDev, TestMailInterface:test_sendMailSingleProduction, TestMailInterface:test_sendMailMultiDev
        :param heading: the subject line for the email to be sent
        :param messageBody: the message body of the email to be sent
        :return: success/failure of the operation
        """
        logging.info("MailInterface:_sendMail called.")

        if self.__sendingMailIsNotPossible():
            return False
        
        self._fromEmailAddress = "app.dev.notifications.tc@gmail.com"

        if self._environment == "production" or True:
            try:

                msg = EmailMessage()
                messageBody = f"etfbot investmentapp run at {datetime.datetime.now()}\n\nLog content:\n\n\n{messageBody}"
                msg.set_content(messageBody)
                msg['Subject'] = f'[etfbot] {heading}'
                msg['From'] = self._fromEmailAddress
                msg['To'] = self._toEmailAddress

                # Send the message via our own SMTP server.
                s = smtplib.SMTP('192.168.0.106')
                s.send_message(msg)
                s.quit()
                logging.info(f"Email sent to {self._toEmailAddress}")
                return True
            except Exception as exception:
                logging.error(exception)
                return False
        elif self._environment == "development":
            logging.info(f"Program is running in {self._environment} mode. No email has been sent.")
            return True
        else:
            logging.info(f"Environment mode: {self._environment} is not recognised.")
            return False

    def __sendingMailIsNotPossible(self):
        """
        __sendingMailIsNotPossible checks that the private members required to send an email are set.
        :testedWith: TestMailInterface:test_sendingMailIsNotPossible
        :return: whether it is possible to send an email with the current configuration of the MailInterface 
        """
        if self._toEmailAddress and self._fromEmailAddress:
            return False

        logging.info(
            f"Sending a notification mail is not possible because at least one of the following values was not provided - toEmailAddress: {self._toEmailAddress}, mailUsername: {self._fromEmailAddress}")
        return True

    ##### Private functions end #####

if __name__== "__main__":
    os.environ["LOGS_DIR"] = "/home/tom/projects/etfbot/webapp/dev_logs"
    mailInterface = MailInterface(enterLogMessage="test sendMail entered", toEmailAddress="tom.connolly@protonmail.com",
                                  environment="production", fromEmailAddress="app.dev.notifications.tc@gmail.com")

    mailInterface.sendInvestmentAppSummaryMail(True)
    pass
