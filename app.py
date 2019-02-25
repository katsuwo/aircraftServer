from flask import Flask, abort, request
from flask_pymongo import PyMongo
import json
import datetime
import Utility
import math
from bson import ObjectId
#
# Pymongo Version 3.4.0 required( newest version is invalid)
#

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/adsb'
mongo = PyMongo(app)

@app.route('/all', methods=['GET'])
def getAllAircrafts():
    aircrafts = mongo.db.aircrafts.find()
    return getJson(aircrafts)

@app.route('/count', methods=['GET'])
def getAircraftsCount():
    aircrafts = mongo.db.aircrafts.find()

    count = 0
    for ac in aircrafts:
        count += 1
    return str(count)


@app.route('/lastupdate/<lastupdatetime>', methods=['GET'])
def getAircraftLastupdate(lastupdatetime = None):
    if lastupdatetime is None:
        return "NONE"
    query = {"update_time_stamp":{'$gte':int(lastupdatetime)}}
    aircrafts = mongo.db.aircrafts.find(query)
    return getJson(aircrafts)


@app.route('/calibration', methods=['POST'])
def calibration():
    print("Calibration")
    data = request.data.decode('utf-8')
    data = json.loads(data)
    data["TimeStamp"] = Utility.getTimeStamp()

    #remove old calibration-data
    col = mongo.db.calibration
    col.drop()

    print(data)
    col = mongo.db.calibration
    col.insert(data)
    retDict = {"result":"OK",
               "statusCode":200}

    return JSONEncoder().encode(retDict)

def getJson(aircrafts):
    acs = {}
    calib ={}
    for ac in aircrafts:
        acs[ac["icao"]] = JSONEncoder().encode(ac)
    readTime = str(math.floor(Utility.getTimeStamp()))
    calibrationDataCollection = mongo.db.calibration.find()
    if calibrationDataCollection.count() == 0:
        calib = "None"
    else:
        calib = calibrationDataCollection[0]
    retDict = {'Items':acs,
               'Calibration': calib,
               'ReadTime':readTime}
    return JSONEncoder().encode(retDict)

def getTimeStamp():
    return datetime.datetime.now().timestamp()

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)

