#!/venv/bin/python

# external dependencies
import unittest
import mock

# internal dependencies
from common.LoggingController import (
    listExistingLogFiles,
    getLatestMainLogContent,
    listExistingMainLogFiles
)
from webapp.server.test.testUtilities import FakeFile


class Test_LoggingController(unittest.TestCase):

    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("common.LoggingController.getLogsDir")
    def test_listExistingLogFiles(self, getLogsDirMock, listdirMock, isfileMock):

        # config mocks
        getLogsDirMock.return_value = "nothing"
        listdirMock.return_value = [
            "etfbot-Main_2024-08-22-18-45.log",
            "etfbot-hello_wewew123_2024-07-23-18-45.log",
            "etfbot_2023-07-23-18-45.log",
            "etfbot-OtherRandom_thing_2024-07-23-18-55.log",
        ]
        isfileMock.return_value = True

        existingLogFiles = listExistingLogFiles()

        expectedExistingLogFiles = [
            "etfbot-Main_2024-08-22-18-45.log",
            "etfbot-OtherRandom_thing_2024-07-23-18-55.log",
            "etfbot-hello_wewew123_2024-07-23-18-45.log",
            "etfbot_2023-07-23-18-45.log",
        ]

        self.assertEqual(expectedExistingLogFiles, existingLogFiles)


    @mock.patch("os.path.isfile")
    @mock.patch("os.listdir")
    @mock.patch("common.LoggingController.getLogsDir")
    def test_listExistingMainLogFiles(self, getLogsDirMock, listdirMock, isfileMock):

        # config mocks
        getLogsDirMock.return_value = "nothing"
        listdirMock.return_value = [
            "etfbot-Main_2024-08-22-18-45.log",
            "etfbot-hello_wewew123_2024-07-23-18-45.log",
            "etfbot-Main_2024-07-23-18-45.log",
            "etfbot-Main_2023-07-23-18-45.log",
            "etfbot-Main_2024-07-23-18-55.log",
        ]
        isfileMock.return_value = True

        existingLogFiles = listExistingMainLogFiles()

        expectedExistingLogFiles = [
            "etfbot-Main_2024-08-22-18-45.log",
            "etfbot-Main_2024-07-23-18-55.log",
            "etfbot-Main_2024-07-23-18-45.log",
            "etfbot-Main_2023-07-23-18-45.log",
        ]

        self.assertEqual(expectedExistingLogFiles, existingLogFiles)


    @mock.patch("builtins.open", create=True)
    @mock.patch("common.LoggingController.listExistingLogFiles")
    def test_getLatestMainLogContent(self, listExistingLogFilesMock, openMock):

        # config mocks
        listExistingLogFilesMock.return_value = [
            "etfbot-Main_2024-08-22-18-45.log",
            "etfbot-OtherRandom_thing_2024-07-23-18-55.log",
            "etfbot-hello_wewew123_2024-07-23-18-45.log",
            "etfbot_2023-07-23-18-45.log",
        ]
        fakeLogContent = """
        some content of a log file

        some more content

        last bit of content

        """
        openMock.return_value = FakeFile(fakeLogContent)

        # testable function
        logContent = getLatestMainLogContent()

        self.assertEqual(fakeLogContent, logContent)


if __name__ == "__main__":
    import sys

    sys.path.append()
    unittest.main()
