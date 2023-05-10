#!/venv/bin/python

# external dependencies
import json
import unittest
import mock
import copy

# internal dependencies
from server.interfaces.MediaIndexFileInterface import loadMediaFile, removeRecordFromMediaInfoFile, updateRecordInMediaInfoFile, writeNewRecordToMediaInfoFile, writeToMediaInfoRecordsFile
from server.test.testUtilities import FakeFile


class Test_MediaIndexFileInterface(unittest.TestCase):


    @mock.patch("builtins.open", create=True)
    @mock.patch("os.getenv")
    def test_loadMediaFile(self, osGetEnvMock, openMock):

        #config fake data
        fakeMediaItems = [
            {
                "mediaName": "fakeMediaName",
                "latestSeason": "1",
                "latestEpisode": "2",
                "blacklistTerms": "blacklistTerm1,blacklistTerm2 , blacklistTerm3  "
            },
            {
                "mediaName": "fakeMediaName",
                "latestSeason": "1",
                "latestEpisode": "2",
                "blacklistTerms": "blacklistTerm1,blacklistTerm2 , blacklistTerm3  "
            }
        ]
        fakeFileContentDict = {
            "media": fakeMediaItems
        }
        fakeFileContent = json.dumps(fakeFileContentDict)
        fakeEnvReturn = "fakeEnvReturn"

        # config mocks
        osGetEnvMock.return_value = fakeEnvReturn
        openMock.return_value = FakeFile(fakeFileContent)

        content = loadMediaFile()

        self.assertEqual(fakeMediaItems, content)
        openMock.assert_called_with(fakeEnvReturn, "r")


    @mock.patch("server.interfaces.MediaIndexFileInterface.writeToMediaInfoRecordsFile")
    @mock.patch("server.interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_writeNewRecordToMediaInfoFile(self, loadMediaFileMock, writeToMediaInfoRecordsFileMock):

        #config fake data
        fakeMediaItems = [
            {
                "name": "fakeName1", 
                "typeSpecificData": {
                    "latestSeason": 1, 
                    "latestEpisode": 2
                },
                "blacklistTerms": ["blacklistTerm1", "blacklistTerm2"]
            },
            {
                "name": "fakeName2", 
                "typeSpecificData": {
                    "latestSeason": 3, 
                    "latestEpisode": 4
                },
                "blacklistTerms": ["blacklistTerm3", "blacklistTerm4"]
            }
        ]
        unchangedFakeMediaItems = copy.copy(fakeMediaItems)
        fakeNewMediaName = "afakeNewMediaName"
        fakeNewMediaLatestSeason = 5
        fakeNewMediaLatestEpisode = 6
        fakeNewMediaLatestBlacklistTerms = [ "fakeNewBlacklistTerm1", "fakeNewBlacklistTerm2"]

        # config mocks
        loadMediaFileMock.return_value = fakeMediaItems

        success = writeNewRecordToMediaInfoFile(fakeNewMediaName, fakeNewMediaLatestSeason, fakeNewMediaLatestEpisode, fakeNewMediaLatestBlacklistTerms)

        # expected data
        newFakeMediaItem = {
            "name": fakeNewMediaName, 
            "typeSpecificData": {
                "latestSeason": fakeNewMediaLatestSeason, 
                "latestEpisode": fakeNewMediaLatestEpisode
            }, 
            "blacklistTerms": fakeNewMediaLatestBlacklistTerms
        }
        expectedFakeMediaItems = [newFakeMediaItem] + unchangedFakeMediaItems

        self.assertEqual(True, success)
        loadMediaFileMock.assert_called()
        writeToMediaInfoRecordsFileMock.assert_called_with(expectedFakeMediaItems)


    @mock.patch("json.dump")
    @mock.patch("builtins.open", create=True)
    @mock.patch("os.getenv")
    def test_writeToMediaInfoRecordsFile(self, osGetEnvMock, openMock, jsonDumpMock):

        #config fake data
        fakeMediaItems = [
            {
                "name": "fakeName1", 
                "typeSpecificData": {
                    "latestSeason": 1, 
                    "latestEpisode": 2
                },
                "blacklistTerms": ["blacklistTerm1", "blacklistTerm2"]
            }
        ]
        fakeFileContentDict = {
            "media": fakeMediaItems
        }
        fakeFileContent = json.dumps(fakeFileContentDict)
        fakeEnvReturn = "fakeEnvReturn"
        fakeFileContent = FakeFile(fakeFileContent)

        # config mocks
        osGetEnvMock.return_value = fakeEnvReturn
        openMock.return_value = fakeFileContent

        writeToMediaInfoRecordsFile(fakeMediaItems)
        

        # asserts
        osGetEnvMock.assert_called_with("MEDIA_INDEX_FILE_LOCATION")
        openMock.assert_called_with(fakeEnvReturn, "w")
        jsonDumpMock.assert_called_with({ "media": fakeMediaItems }, fakeFileContent)


    @mock.patch("server.interfaces.MediaIndexFileInterface.writeToMediaInfoRecordsFile")
    @mock.patch("server.interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_removeRecordFromMediaInfoFile(self, loadMediaFileMock, writeToMediaInfoRecordsFileMock):

        #config fake data
        fakeMediaItems = [
            {
                "name": "fakeName1", 
                "typeSpecificData": {
                    "latestSeason": 1, 
                    "latestEpisode": 2
                },
                "blacklistTerms": ["blacklistTerm1", "blacklistTerm2"]
            },
            {
                "name": "fakeName2", 
                "typeSpecificData": {
                    "latestSeason": 3, 
                    "latestEpisode": 4
                },
                "blacklistTerms": ["blacklistTerm3", "blacklistTerm4"]
            }
        ]
        fakeRecordIndex = 0
        unchangedFakeMediaItems = copy.copy(fakeMediaItems)

        # config mocks
        loadMediaFileMock.return_value = fakeMediaItems

        success = removeRecordFromMediaInfoFile(fakeRecordIndex)

        self.assertEqual(True, success)
        loadMediaFileMock.assert_called()
        writeToMediaInfoRecordsFileMock.assert_called_with(unchangedFakeMediaItems[1:])


    @mock.patch("server.interfaces.MediaIndexFileInterface.writeToMediaInfoRecordsFile")
    @mock.patch("server.interfaces.MediaIndexFileInterface.loadMediaFile")
    def test_updateRecordInMediaInfoFile(self, loadMediaFileMock, writeToMediaInfoRecordsFileMock):

        #config fake data
        fakeMediaItems = [
            {
                "name": "fakeName1", 
                "typeSpecificData": {
                    "latestSeason": 1, 
                    "latestEpisode": 2
                },
                "blacklistTerms": ["blacklistTerm1", "blacklistTerm2"]
            },
            {
                "name": "fakeName2", 
                "typeSpecificData": {
                    "latestSeason": 3, 
                    "latestEpisode": 4
                },
                "blacklistTerms": ["blacklistTerm3", "blacklistTerm4"]
            }
        ]
        fakeRecordIndex = 1
        expectedFakeMediaItems = copy.copy(fakeMediaItems)
        newFakeMediaItem = {
            "name": "fakeName3", 
            "typeSpecificData": {
                "latestSeason": 5, 
                "latestEpisode": 6
            },
            "blacklistTerms": ["blacklistTerm5", "blacklistTerm6"]
        }
        expectedFakeMediaItems[1] = newFakeMediaItem

        # config mocks
        loadMediaFileMock.return_value = fakeMediaItems

        success = updateRecordInMediaInfoFile(newFakeMediaItem, fakeRecordIndex)

        self.assertEqual(True, success)
        loadMediaFileMock.assert_called()
        writeToMediaInfoRecordsFileMock.assert_called_with(expectedFakeMediaItems)

