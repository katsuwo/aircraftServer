from flask import Flask
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

def getJson(aircrafts):
    acs = {}
    for ac in aircrafts:
        acs[ac["icao"]] = JSONEncoder().encode(ac)
    readTime = str(math.floor(Utility.getTimeStamp()))
    retDict = {'Items':acs,
               'ReadTime':readTime}
    return JSONEncoder().encode(retDict)

def getTimeStamp():
    return datetime.datetime.now().timestamp()

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)

