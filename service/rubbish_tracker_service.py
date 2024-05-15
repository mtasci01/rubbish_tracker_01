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
from shapely.geometry.polygon import Polygon

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

    def getRightnowUTC(self):
        return round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
    #todo enum
    def isRole(self,role):
        if (role.upper() == "ADMIN" or role.upper() == "REPORTER"):
            return True
        return False
    
    def createReport(self,lat,lon,desc,userId):
        user = db.users.find_one({'_id': ObjectId(userId)})
        if (user) is None:
            raise TypeError("userId not found ")
        rightnowUTC = self.getRightnowUTC()
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
        rightnowUTC = self.getRightnowUTC()
        user['createdAtUTC']=rightnowUTC
        if not(self.isRole(role)):
            raise TypeError("role not found " + role)
        user['role'] = role.upper()
        db.users.insert_one(user)
        logging.info("created user with id " + str(user["_id"]))  

    def deleteReport(self,reportId):
        db.reports.delete_one({'_id': ObjectId(reportId)})
        logging.info("deleted report with id " + str(reportId))  

    def fixReport(self, reportId, when):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            raise TypeError("reportId not found " + reportId)  
        db.reports.find_one_and_update(
            {"_id" : ObjectId(reportId)},
            {"$set":
                {"fixedAtUTC": when}
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
    
    def saveArea(self,points, areaName, areaId):
        poly = Polygon(points)
        polyarea = poly.area
        if polyarea <= 0:
            raise TypeError("invalid polygon for " + areaName + ". Order matters")
        rightnowUTC = self.getRightnowUTC()
        
        area2Save = {
            "areaName":areaName,
            "points":points,
            "savedAtUTC":rightnowUTC,
            "polyArea":polyarea
        }
        if not(areaId is None):
            area = db.areas.find_one({'_id': ObjectId(areaId)})
            if not((area) is None):
                area2Save['_id'] = ObjectId(areaId)
                db.areas.delete_one({'_id': ObjectId(areaId)})

        db.areas.insert_one(area2Save)
        logging.info("saved area id" + str(area2Save['_id'])) 

    def getArea(self, areaId):
        return self.parse_json(db.areas.find_one({'_id': ObjectId(areaId)}))
    
    def getAreas(self):
        return self.parse_json(list(db.areas.find({})))
    
    def deleteArea(self,areaId):
        db.areas.delete_one({'_id': ObjectId(areaId)})
        logging.info("run delete area doc with id " + str(areaId)) 

    def createReports(self,reports, userId):
        user = db.users.find_one({'_id': ObjectId(userId)})
        if (user) is None:
            raise TypeError("userId not found " + userId)
        
        reports2Save = []
        for report in reports:
            report2Save = {}
            report2Save["lat"] = report["lat"]
            report2Save["lon"] = report["lon"]
            report2Save["desc"] = report["desc"]
            report2Save['user'] = DBRef("users", ObjectId(user["_id"]))
            report2Save['createdAtUTC'] = report['createdAt']
            reports2Save.append(report2Save)
        db.reports.insert_many(reports2Save)
        logging.info("created reports n " + str(len(reports2Save)))  

    def randomPointsInCircle(self, center, radius, numOfPoints):
        points = []
        for i in range(numOfPoints):
            r = radius * random.uniform(0, 1)
            theta = random.uniform(0, 1) * 2 * np.pi
            x =  r * np.cos(theta)
            y =  r * np.sin(theta)
            point = np.array([x,y])
            point = point + np.array(center)
            points.append(point)  
        return points     

    def downloadReportImg(self,imgId):
        record = db.images.find_one({'_id': ObjectId(imgId)})
        if (record) is None:
            raise TypeError("imgId not found " + imgId)
        return {"imgBytes":pickle.loads(record["img"]), "filename":record["filename"]}  

    def deleteReportImg(self,imgId):
        db.images.delete_one({'_id': ObjectId(imgId)})
        logging.info("run delete img doc with id " + str(imgId)) 

    #todo with gridfs
    def saveReportPicture(self, filename, reportId):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            raise TypeError("reportId not found " + reportId) 
        rightnowUTC = self.getRightnowUTC()
        pictures = []
        if 'pictures' in report:
            pictures = report['pictures']             
        with open(filename, 'rb') as f:
            contents = f.read()
            doc = {
                "img": bson.Binary(pickle.dumps(contents)),
                "filename":filename,
                "createdAtUTC":rightnowUTC
            }
            db.images.insert_one(doc)
            logging.info("created img wwith id " + str(doc["_id"]))
            pictures.append(DBRef("images",ObjectId(doc["_id"])))   
        
        db.reports.find_one_and_update(
            {"_id" : ObjectId(reportId)},
            {"$set":
                {"pictures": pictures}
            },upsert=False
        )
        #self.deleteReportImg(oldImgId)    
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
    
    def randomPointsinPolygon(self,polygon, number):
        points = []
        minx, miny, maxx, maxy = polygon.bounds
        while len(points) < number:
            p0 = np.random.uniform(minx, maxx)
            p1 = np.random.uniform(miny, maxy)
            pnt = Point(p0, p1)
            if polygon.contains(pnt):
                points.append([p0,p1])
        return points


    


    

    



       