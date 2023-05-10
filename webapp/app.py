#!/venv/bin/python

# external dependencies
from flask import Flask, request, Response, send_from_directory
from dotenv import load_dotenv
from os.path import join, dirname
import os
import json

# internal dependencies
from server.controllers.PageServer import serveIndex
from server.controllers.DataServer import serveMediaInfo, submitMediaInfoRecord, deleteMediaInfoRecord, updateMediaInfoRecord, runMediaGrab, getSimilarShows

#create app
app = Flask(__name__, template_folder="client")

# load env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def getResponse(errorCode, message):
    return Response(message, status=errorCode, mimetype="text/html") 


@app.route("/", methods=["GET"])
def index():
    return serveIndex()


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'client/images'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/runInvestmentBalancer", methods=["GET"])
def MediaInfoRecords():
        return serveMediaInfo()



# @app.route('/runInvestmentBalancer', methods=["GET"])
# def mediaGrab():
#     if runMediaGrab():
#         return getResponse(200, "run media grab accepted") 
#     else:
#         return getResponse(500, "run media grab failed") 



if __name__ == "__main__":
    app.run(host="0.0.0.0")
