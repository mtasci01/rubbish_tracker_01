import datetime
import json
import pickle
import random
from bson import DBRef, ObjectId
import bson
import numpy as np
import pymongo
import logging
from bson import json_util
import gridfs
from shapely.geometry import Point
import configparser

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
 
    # Read the configuration file
    config.read('config.ini')
 
    # Access values from the configuration file
 
    # Return a dictionary with the retrieved values
    config_values = {
        'mongo_connstr': config.get('General', 'mongo_connstr'),
        'mongo_db': config.get('General', 'mongo_db')
    }
 
    return config_values

config = read_config()

mongoclient = pymongo.MongoClient(config['mongo_connstr'])
db = mongoclient[config['mongo_db']]
fs = gridfs.GridFS(db)
logging.basicConfig(level=logging.INFO)


class RubbishTrackerService:

    #todo enum
    def isRole(self,role):
        if (role.upper() == "ADMIN" or role.upper() == "REPORTER"):
            return True
        return False
    
    def createReport(self,lat,lon,desc,userId):
        user = db.users.find_one({'_id': ObjectId(userId)})
        if (user) is None:
            raise TypeError("userId not found ")
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
        report = {}
        report['user'] = DBRef("users", ObjectId(user["_id"]))
        report['createdAtUTC'] = rightnowUTC
        report['lat'] = lat
        report['lon'] = lon
        report['desc'] = desc
        db.reports.insert_one(report)
        logging.info("created report with id " + str(report["_id"]))  
    
    def createUser(self,name,role):
        if (name) is None:
            raise TypeError("createUser(): name null ")
        user = {}
        user['name'] = name
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
        user['createdAtUTC']=rightnowUTC
        if not(self.isRole(role)):
            raise TypeError("role not found " + role)
        user['role'] = role.upper()
        db.users.insert_one(user)
        logging.info("created user with id " + str(user["_id"]))  

    def deleteReport(self,reportId):
        db.reports.delete_one({'_id': ObjectId(reportId)})
        logging.info("deleted report with id " + str(reportId))  

    def fixReport(self, reportId):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            raise TypeError("reportId not found " + reportId)  
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
        db.reports.find_one_and_update(
            {"_id" : ObjectId(reportId)},
            {"$set":
                {"fixedAtUTC": rightnowUTC}
            },upsert=False
        )
        logging.info("fixed report with id " + str(reportId))  

    def getUsers(self):
        return self.parse_json(list(db.users.find({})))

    def parse_json(self, data):
        return json.loads(json_util.dumps(data)) 
    
    def getReport(self,reportId):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            return {}
        report['username'] = db.dereference(report['user'])['name']
        return self.parse_json(report)
    
    def getLiveReports(self):
        return self.parse_json(list(db.reports.find({"fixedAtUTC":None})))
    
    def getAllReports(self):
        return self.parse_json(list(db.reports.find({})))
    
    def createReports(self,reports, userId):
        user = db.users.find_one({'_id': ObjectId(userId)})
        if (user) is None:
            raise TypeError("userId not found " + userId)
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
        reports2Save = []
        for report in reports:
            report2Save = {}
            report2Save["lat"] = report["lat"]
            report2Save["lon"] = report["lon"]
            report2Save["desc"] = report["desc"]
            report['user'] = DBRef("users", ObjectId(user["_id"]))
            report['createdAtUTC'] = rightnowUTC
            reports2Save.append(report2Save)
        db.reports.insert_many(reports)
        logging.info("created reports n " + str(len(reports2Save)))  

    def randomReportsInRome(self, numOfPoints, userId,):
        if numOfPoints < 3:
            raise TypeError("pass at least 3 numOfPoints")
        # rubbish in rome, we generate at random more rubbish in the center
        nwCorner = [12.358505, 41.981065]
        seCorner = [12.610007, 41.791397]
        horizontalSide = seCorner[0] - nwCorner[0]
        verticalSide = nwCorner[1] - seCorner[1]
        center = [(horizontalSide)/2 + nwCorner[0], (verticalSide)/2 + seCorner[1]]
        minSide = horizontalSide
        if (verticalSide < minSide):
            minSide = verticalSide
        radius = minSide* 0.4

        points = []
        for i in range(numOfPoints):
            if (random.uniform(0, 1) > 0.2):
                r = radius * random.uniform(0, 1)
                theta = random.uniform(0, 1) * 2 * np.pi
                x =  r * np.cos(theta)
                y =  r * np.sin(theta)
                point = np.array([x,y])
                point = point + np.array(center)
            else:
                x = random.uniform(nwCorner[0], seCorner[0])
                y = random.uniform(seCorner[1], nwCorner[1])
                point = np.array([x,y])
            
            points.append(point)

        reports2Save = []
        i = 0
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
        for point in points:
            reqJsonO = {"lat":point[1], "lon":point[0], "desc":"rubbish report " + str(rightnowUTC) + "_" + str(i)}
            reports2Save.append(reqJsonO)
            i = i + 1
        self.createReports(reports2Save, userId)

    def downloadReportImg(self,imgId):
        record = db.images.find_one({'_id': ObjectId(imgId)})
        if (record) is None:
            raise TypeError("imgId not found " + imgId)
        return {"imgBytes":pickle.loads(record["img"]), "filename":record["filename"]}  

    def deleteReportImg(self,imgId):
        db.images.delete_one({'_id': ObjectId(imgId)})
        logging.info("deleted img doc with id " + str(imgId)) 

    #todo with gridfs
    def saveReportPicture(self, filename, reportId):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            raise TypeError("reportId not found " + reportId) 
        rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000) 
        oldImgId = db.dereference(report['picture'])['_id']
        with open(filename, 'rb') as f:
            contents = f.read()
            doc = {
                "img": bson.Binary(pickle.dumps(contents)),
                "filename":filename,
                "createdAtUTC":rightnowUTC

            }
            db.images.insert_one(doc)

        db.reports.find_one_and_update(
            {"_id" : ObjectId(reportId)},
            {"$set":
                {"picture": DBRef("images",ObjectId(doc["_id"]))}
            },upsert=False
        )
        self.deleteReportImg(oldImgId)    
        logging.info("saved file " + filename + " for reportid " + reportId)  

    def countReportsInPolygon(self,polygon, reports):
        result = {"tot":0,"contained":0}
        for report in reports:
            point = Point(report['lon'], report['lat'])
            #point = Point(12.0, 42.0)
            #print(point)
            
            if polygon.contains(point):
                result['contained'] = result['contained'] + 1
            result['tot'] = result['tot'] + 1
        return result

    def getLiveReportsByDay(self):
        results = db.reports.aggregate([
        { "$match" : { "fixedAtUTC" : None }},
        { 
        "$project" : { "_id" : 1,
        "toDate": {
        "$toDate": "$createdAtUTC"
        } } },
        {"$project" : { "_id" : 1,
        "year": { "$year": "$toDate" },
        "month": { "$month": "$toDate" },
        "day": { "$dayOfMonth": "$toDate" } }},
        { "$group" : { "_id":{"year":"$year", "month":"$month", "day":"$day"}, "totaldocs" : { "$sum" : 1 } } }
        ])
        l = []
        for m in results:
            l.append(m)
        return l    


    


    

    



       