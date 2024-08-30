#!/venv/bin/python

# external dependencies
import datetime
from unittest.mock import MagicMock
import unittest
import mock
import random

# internal dependencies
from server.controllers.LoggingController import listExistingLogFiles, getLatestLogContent
from server.test.testUtilities import FakeFile


class Test_LoggingController(unittest.TestCase):

    @mock.patch('os.path.isfile')
    @mock.patch('os.listdir')
    @mock.patch("server.controllers.LoggingController.getLogsDir")
    def test_listExistingLogFiles(self, getLogsDirMock, listdirMock, isfileMock):
        
        # config mocks
        getLogsDirMock.return_value = "nothing"
        listdirMock.return_value = [
            "etfbot-Main_22-08-2024_18-45.log",
            "etfbot-hello_wewew123_23-07-2024_18-45.log",
            "etfbot_23-07-2023_18-45.log",
            "etfbot-OtherRandom_thing_23-07-2024_18-55.log"
        ]
        isfileMock.return_value = True

        existingLogFiles = listExistingLogFiles()

        expectedExistingLogFiles = [
            "etfbot-Main_22-08-2024_18-45.log",
            "etfbot-OtherRandom_thing_23-07-2024_18-55.log",
            "etfbot-hello_wewew123_23-07-2024_18-45.log",
            "etfbot_23-07-2023_18-45.log"
        ]

        self.assertEqual(expectedExistingLogFiles, existingLogFiles)


    @mock.patch("builtins.open", create=True)
    @mock.patch("server.controllers.LoggingController.listExistingLogFiles")
    def test_listExistingLogFiles(self, listExistingLogFilesMock, openMock):
        
        # config mocks
        listExistingLogFilesMock.return_value = [
            "etfbot-Main_22-08-2024_18-45.log",
            "etfbot-OtherRandom_thing_23-07-2024_18-55.log",
            "etfbot-hello_wewew123_23-07-2024_18-45.log",
            "etfbot_23-07-2023_18-45.log"
        ]
        fakeLogContent = '''
        some content of a log file

        some more content

        last bit of content

        '''
        openMock.return_value = FakeFile(fakeLogContent)

        # testable function
        logContent = getLatestLogContent()

        self.assertEqual(fakeLogContent, logContent)        


if __name__ == "__main__":
    unittest.main()