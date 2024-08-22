#!/venv/bin/python

# external dependencies
import datetime
from unittest.mock import MagicMock
import unittest
import mock
import random

# internal dependencies
from server.controllers.LoggingController import listExistingLogFiles


class Test_LoggingController(unittest.TestCase):

    ##### helper functions start ######


    
    
    ##### helper functions end ######

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch("server.controllers.LoggingController.getLogsDir")
    def test__getLastYearDates(self, getLogsDirMock, listdirMock, isfileMock):
        
        # config mocks
        getLogsDirMock.return_value = "nothing"
        listdirMock.return_value = [
            "etfbot_22-08-2024_18-45.log",
            "etfbot_23-07-2024_18-45.log",
            "etfbot_23-07-2023_18-45.log",
            "etfbot_23-07-2024_18-55.log"
        ]
        isfileMock.return_value = True

        existingLogFiles = listExistingLogFiles()

        expectedExistingLogFiles = [
            "etfbot_22-08-2024_18-45.log",
            "etfbot_23-07-2024_18-55.log",
            "etfbot_23-07-2024_18-45.log",
            "etfbot_23-07-2023_18-45.log"
        ]

        self.assertEqual(expectedExistingLogFiles, existingLogFiles)


if __name__ == "__main__":
    unittest.main()