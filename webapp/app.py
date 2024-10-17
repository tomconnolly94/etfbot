#!/venv/bin/python

# external dependencies
from flask import Flask, Response, send_from_directory, request
from dotenv import load_dotenv
from os.path import join, dirname
import json
import os, sys
import logging

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # make investmentapp and common sub projects accessible
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    + "/investmentapp"
)  # make investmentapp and common sub projects accessible

# internal dependencies
from webapp.server.controllers.PageServer import serveIndex
from webapp.server.controllers.DataServer import (
    getInvestmentData,
    runInvestmentBalancer,
    getExcludeList,
    removeExcludeListItem,
    addExcludeListItem,
    getCompletedOrderDataBySymbol,
    getCurrentStockPrice,
)
from common import LoggingController

# create app
app = Flask(__name__, template_folder="client")

# load env file
dotenv_path = join(dirname(__file__), ".env")
investmentapp_dotenv_path = join("../investmentapp", ".env")
load_dotenv(dotenv_path)
load_dotenv(investmentapp_dotenv_path)

LoggingController.initLogging(forceStdoutLogging=True)

logging.info(f"Program started.")


def getResponse(errorCode, message, mimetype="text/html"):
    return Response(message, status=errorCode, mimetype=mimetype)


@app.route("/", methods=["GET"])
def index():
    return serveIndex()


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "client/images"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/getInvestmentPerformanceData", methods=["GET"])
def getInvestmentPerformanceData():
    return getInvestmentData()


@app.route("/runInvestmentBalancer", methods=["GET"])
def mediaGrab():
    logs = runInvestmentBalancer()
    if logs:
        returnData = {"message": "investment app run successful", "logs": logs}
        logging.info(returnData)
        return getResponse(200, json.dumps(returnData), "application/json")
    else:
        return getResponse(500, "investment app run failed")


@app.route("/excludeList/<stockSymbol>", methods=["POST", "DELETE"])
def excludeListItem(stockSymbol):
    try:
        if request.method == "DELETE":
            if removeExcludeListItem(stockSymbol):
                return getResponse(200, "ExcludeList item deleted successfully")
            else:
                return getResponse(500, "ExcludeList item failed to delete")
        elif request.method == "POST":
            excludeReason = request.args["reason"]
            if addExcludeListItem(stockSymbol, excludeReason):
                return getResponse(200, "ExcludeList item added successfully")
            else:
                return getResponse(500, "ExcludeList item failed to add")
        else:
            return getResponse(405, "Method Not Allowed")
    except Exception as exception:
        logging.error(exception)
        return getResponse(500, "Unknown error, check server logs")


@app.route("/excludeList", methods=["GET"])
def excludeList():
    try:
        return getExcludeList()
    except Exception as exception:
        logging.error(exception)
        return getResponse(500, "Unknown error, check server logs")


@app.route("/logFileNames", methods=["GET"])
def logFileNames():
    try:
        return LoggingController.listExistingLogFiles()
    except Exception as exception:
        logging.error(exception)
        return getResponse(500, "Unknown error, check server logs")


@app.route("/symbolOrderInfo", methods=["GET"])
def symbolOrderInfo():
    try:
        return getCompletedOrderDataBySymbol(
            request.args.get("earliestTimestamp"),
            request.args.get("latestTimestamp"),
        )
    except Exception as exception:
        logging.error(exception)
        return getResponse(500, "Unknown error, check server logs")


@app.route("/currentPrice/<stockSymbol>", methods=["GET"])
def currentPrice(stockSymbol):
    try:
        return getCurrentStockPrice(stockSymbol)
    except Exception as exception:
        logging.error(exception)
        return getResponse(500, "Unknown error, check server logs")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
