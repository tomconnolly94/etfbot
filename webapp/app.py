#!/venv/bin/python

# external dependencies
from flask import Flask, Response, send_from_directory
from dotenv import load_dotenv
from os.path import join, dirname
import json
import os
from server.controllers import LoggingController
import logging

# internal dependencies
from server.controllers.PageServer import serveIndex
from server.controllers.DataServer import getInvestmentData, runInvestmentBalancer, getExcludeList

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


@app.route("/getExcludeListData", methods=["GET"])
def getExcludeListData():
        return getExcludeList()



if __name__ == "__main__":
    app.run(host="0.0.0.0")
