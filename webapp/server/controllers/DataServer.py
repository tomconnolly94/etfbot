#!/venv/bin/python

# external dependencies
import json
import os
import subprocess

# internal dependencies
from server.interfaces.MediaIndexFileInterface import removeRecordFromMediaInfoFile, updateRecordInMediaInfoFile, writeNewRecordToMediaInfoFile
from server.interfaces import TheMovieDatabaseInterface


def serveMediaInfo():
    file = open(os.getenv("MEDIA_INDEX_FILE_LOCATION"), "r")
    mediaIndexFile = json.loads(file.read())
    # return TheMovieDatabaseInterface.getInstance().addShowReccomendationsToMediaIndexContent(mediaIndexFile)
    return mediaIndexFile


def submitMediaInfoRecord(data):

    # extract data
    mediaName = data['mediaName']
    latestSeason = int(data['latestSeason'])
    latestEpisode = int(data['latestEpisode'])
    blacklistTerms = data['blacklistTerms']

    blacklistTerms = [ term.replace(" ", "") for term in blacklistTerms.split(",") if len(term) > 0]

    success = writeNewRecordToMediaInfoFile(mediaName, latestSeason, latestEpisode, blacklistTerms)

    return success


def deleteMediaInfoRecord(recordIndex):
    return removeRecordFromMediaInfoFile(recordIndex)


def updateMediaInfoRecord(newMediaIndexRecord, recordIndex):
    newMediaIndexRecord = json.loads(newMediaIndexRecord)

    return updateRecordInMediaInfoFile(newMediaIndexRecord, recordIndex)


def runMediaGrab():
    mediaGrabDir = os.getenv("MEDIA_GRAB_DIRECTORY")

    subprocess.check_call(['./Main.py'], cwd=mediaGrabDir)

    return True


def getSimilarShows(showTitle):
    return TheMovieDatabaseInterface.getInstance().getSimilarShowTitles(showTitle)
