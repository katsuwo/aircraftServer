from flask import Flask, abort, request
from flask_pymongo import PyMongo
import json
import datetime
import Utility
import xlrd
from ACCSectorReader import ACCSectorReader

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

ACCSectorReader().getAllSectors()


@app.route('/accsectors', methods=['GET'])
def getACCSectors():
    sector = ACCSectorReader().getAllSectors()
    return JSONEncoder().encode(sector)

@app.route('/airports', methods=['GET'])
def getAllAirports():
    airports = mongo.db.airports.find()
    return getJson(airports)

@app.route('/all', methods=['GET'])
def getAllAircrafts():
    aircrafts = mongo.db.aircrafts.find()
    return getJson(aircrafts)

@app.route('/clear', methods=['GET'])
def clearDatabase():
    mongo.db.aircrafts.drop()
    aircrafts = mongo.db.aircrafts.find()
    return getJson(aircrafts)

@app.route('/remove', methods=['GET'])
def removeAircrafts(lastupdatetime = None):
    query = {"update_time_stamp":{'$lte':float(lastupdatetime)}}
    return mongo.db.aircrafts.remove(query)

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
    query = {"update_time_stamp":{'$gte':float(lastupdatetime)}}
    aircrafts = mongo.db.aircrafts.find(query)
    return getJson(aircrafts)

@app.route('/interpolation/<val>', methods=['GET'])
def setInterpolation(val="True"):
    interpolation = {}
    if val == "true" or val == "True":
        interpolation = {"Value": True}
    elif val == "False" or val == "false":
        interpolation = {"Value": False}
    else:
        return "Value must be True(true) / False(false)"
    mongo.db.interpolation.drop()
    mongo.db.interpolation.insert(interpolation)
    retDict = {"result": "OK",
               "statusCode": 200,
               "interpolation": interpolation}
    return JSONEncoder().encode(retDict)

@app.route('/trim/<val>', methods=['GET'])
def setTrim(val = None):
    print(val)
    if val is None:
        return "NONE"
    trim = {"Value": val}
    mongo.db.trim.drop()
    mongo.db.trim.insert(trim)

    retDict = {"result": "OK",
               "statusCode": 200,
               "trim": trim}
    return JSONEncoder().encode(retDict)

@app.route('/correction/<direction>/<val>', methods=['GET'])
def setCorrection(direction = None, val = None):
    print(direction)
    if direction is None:
        return "NONE"
    if direction != "altitude" and direction != "forward":
        return "usage: http://xx.xx.xx:yyyy/correction/altitude/zzz  or /correction/forward/zzz"

    if val is not None:
        corrections = mongo.db.correction.find()
        correction = {}
        if corrections.count() == 0:
            correction["altitude"] = 0
            correction["forward"] = 0
            correction[direction] = val
        else:
            correction = corrections[0]
            correction[direction] = val
        mongo.db.correction.drop()
        mongo.db.correction.insert(correction)

        retDict = {"result": "OK",
                   "statusCode": 200,
                   "correction":correction}
        return JSONEncoder().encode(retDict)
    else:
        return  ""
#        query = {"update_time_stamp": {'$gte': float(lastupdatetime)}}


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
    readTime = str(Utility.getTimeStamp())
    calibrationDataCollection = mongo.db.calibration.find()
    if calibrationDataCollection.count() == 0:
        calib = "None"
    else:
        calib = calibrationDataCollection[0]

    corrections = mongo.db.correction.find()
    if corrections.count() == 0:
        correction = {}
        correction["altitude"] = 0
        correction["forward"] = 0
    else:
        correction = corrections[0]

    interpolations = mongo.db.interpolation.find()
    if interpolations.count() == 0:
        interpolation = {}
        interpolation["Value"] = False
    else:
        interpolation = interpolations[0]

    trims = mongo.db.trim.find()
    if trims.count() == 0:
        trim = {}
        trim["Value"] = 0
    else:
        trim = trims[0]

    retDict = {'Items':acs,
               'Calibration': calib,
               'Correction': correction,
               'Interpolation': interpolation,
               'Trim': trim,
               'ReadTime': readTime}
    return JSONEncoder().encode(retDict)

def getTimeStamp():
    return datetime.datetime.now().timestamp()

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)

