#!/venv/bin/python

# external dependencies
from flask import Flask, Response, send_from_directory, request
from dotenv import load_dotenv
from os.path import join, dirname
import json
import os
from server.controllers import LoggingController
import logging

# internal dependencies
from server.controllers.PageServer import serveIndex
from server.controllers.DataServer import getInvestmentData, runInvestmentBalancer, getExcludeList, removeExcludeListItem

#create app
app = Flask(__name__, template_folder="client")

# load env file
dotenv_path = join(dirname(__file__), '.env')
investmentapp_dotenv_path = join("../investmentapp", '.env')
load_dotenv(dotenv_path)
load_dotenv(investmentapp_dotenv_path)


LoggingController.initLogging()

logging.info(f"Program started.")

def getResponse(errorCode, message, mimetype="text/html"):
    return Response(message, status=errorCode, mimetype=mimetype) 


@app.route("/", methods=["GET"])
def index():
    return serveIndex()


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'client/images'),
                          'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/getInvestmentPerformanceData", methods=["GET"])
def getInvestmentPerformanceData():
        return getInvestmentData()


@app.route('/runInvestmentBalancer', methods=["GET"])
def mediaGrab():
    logs = runInvestmentBalancer()
    if logs:
        returnData = { 
            "message": "investment app run successful",
            "logs": logs
        }
        logging.info(returnData)
        return getResponse(200, json.dumps(returnData), "application/json") 
    else:
        return getResponse(500, "investment app run failed") 


@app.route("/excludeList/<stockSymbol>", methods=["POST", "DELETE"])
def excludeListItem(stockSymbol):
    if request.method == 'DELETE':
        if removeExcludeListItem(stockSymbol):
            return getResponse(200, "ExcludeList item deleted successfully") 
        else:
            return getResponse(500, "ExcludeList item failed to delete") 


@app.route("/excludeList", methods=["GET"])
def excludeList():
    return getExcludeList()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
