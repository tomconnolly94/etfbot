#!/venv/bin/python

# external dependencies
import json
from server.test.testUtilities import FakeFile
import unittest
import mock

# internal dependencies
from server.controllers.DataServer import deleteMediaInfoRecord, runMediaGrab, serveMediaInfo, submitMediaInfoRecord, updateMediaInfoRecord


class Test_DataServer(unittest.TestCase):

    @mock.patch("os.getenv")
    @mock.patch("builtins.open", create=True)
    def test_serveMediaInfo(self, openMock, osGetEnvMock):

        #config fake data
        fakeFileContent = "fakeFileContent"

        # config mocks
        osGetEnvMock.return_value = "fake env return"
        openMock.return_value = FakeFile(fakeFileContent)

        content = serveMediaInfo()

        self.assertEqual(fakeFileContent, content)
        

    @mock.patch("server.controllers.DataServer.writeNewRecordToMediaInfoFile")
    def test_submitMediaInfoRecord(self, writeNewRecordToMediaInfoFileMock):

        #config fake data
        fakeData = {
            "mediaName": "fakeMediaName",
            "latestSeason": "1",
            "latestEpisode": "2",
            "blacklistTerms": "blacklistTerm1,blacklistTerm2 , blacklistTerm3  "
        }

        expectedMediaName = "fakeMediaName"
        expectedLatestSeason = 1
        expectedLatestEpisode = 2
        expectedBlacklistTerms = ["blacklistTerm1", "blacklistTerm2", "blacklistTerm3" ]

        # config mock
        writeNewRecordToMediaInfoFileMock.return_value = True
        
        result = submitMediaInfoRecord(fakeData)

        self.assertEqual(True, result)
        writeNewRecordToMediaInfoFileMock.assert_called_with(expectedMediaName, expectedLatestSeason, expectedLatestEpisode, expectedBlacklistTerms)


    @mock.patch("server.controllers.DataServer.removeRecordFromMediaInfoFile")
    def test_deleteMediaInfoRecord(self, removeRecordFromMediaInfoFileMock):

        # config fake data
        recordIndex = "2"

        # config mock
        removeRecordFromMediaInfoFileMock.return_value = True
        
        result = deleteMediaInfoRecord(recordIndex)

        self.assertEqual(True, result)
        removeRecordFromMediaInfoFileMock.assert_called_with(recordIndex)


    @mock.patch("server.controllers.DataServer.updateRecordInMediaInfoFile")
    def test_updateMediaInfoRecord(self, updateRecordInMediaInfoFileMock):

        # config fake data
        fakeNewMediaIndexRecord = {
            "name": "fakeMediaIndexRecordName",
            "latestEpisode": 2,
            "latestSeason": 3,
            "blacklistTerms": ["blacklistTerm1", "blacklistTerm1"]
        }
        fakeStringifiedNewMediaIndexRecord = json.dumps(fakeNewMediaIndexRecord)
        fakeRecordIndex = 2

        # config mock
        updateRecordInMediaInfoFileMock.return_value = True
        
        result = updateMediaInfoRecord(fakeStringifiedNewMediaIndexRecord, fakeRecordIndex)

        self.assertEqual(True, result)
        updateRecordInMediaInfoFileMock.assert_called_with(fakeNewMediaIndexRecord, fakeRecordIndex)


    @mock.patch("subprocess.check_call")
    @mock.patch("os.getenv")
    def test_runMediaGrab(self, osGetEnvMock, checkCallMock):

        # config fake data
        fakeOsGetEnvValue = "fakeOsGetEnvValue"

        # config mock
        osGetEnvMock.return_value = "fakeOsGetEnvValue"

        result = runMediaGrab()


        checkCallMock.assert_called_with(['venv/bin/python', 'Main.py'], cwd=fakeOsGetEnvValue)




if __name__ == "__main__":
    unittest.main()