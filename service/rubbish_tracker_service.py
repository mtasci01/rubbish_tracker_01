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

    def findSlopeYIntercept(self,x1,y1,x2,y2):
        m = (y2-y1)/(x2-x1)
        b = y2 - m*x2
        return m,b

    def printEpoch(self,epochMillis):
        return datetime.datetime.fromtimestamp(epochMillis/1000).strftime('%c')

    def writeFile(self,filename, json2Write):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json2Write, f, ensure_ascii=False, indent=4)
        print("created filename -> " + filename)
    
    def writeBinaryFile(self, filename, theBytes):
        with open(filename, "wb") as binary_file:
            binary_file.write(theBytes)   
        print("created filename -> " + filename)          

    def getRightnowUTC(self):
        return round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)
    
    def createReport(self,lat,lon,desc):
    
        rightnowUTC = self.getRightnowUTC()
        report = {}
        report['createdAtUTC'] = rightnowUTC
        report['lat'] = lat
        report['lon'] = lon
        report['desc'] = desc
        report['pictures']=[]
        db.reports.insert_one(report)
        logging.info("created report with id " + str(report["_id"]))  

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

    def bulkFixReport(self, reports):
        bulk_ops_arr = []

        for report in reports:
            u = pymongo.UpdateOne({"_id": ObjectId(report["_id"]["$oid"])}, {"$set": {"fixedAtUTC": int(report['fixedAtUTC']/1000)*1000}})
            bulk_ops_arr.append(u)
        db.reports.bulk_write(bulk_ops_arr)
        print("fixed num reports: " + str(len(bulk_ops_arr)))

    def parse_json(self, data):
        return json.loads(json_util.dumps(data)) 
    
    def getReport(self,reportId):
        report = db.reports.find_one({'_id': ObjectId(reportId)})
        if (report) is None:
            return {}
        return self.parse_json(report)
    
    def getLiveReports(self):
        
        return self.parse_json(list(db.reports.find({"fixedAtUTC":None})))
    
    def getFixedReports(self):
        return self.parse_json(list(db.reports.find({"fixedAtUTC":{"$ne":None}})))
    
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

    def createReports(self,reports):
        
        reports2Save = []
        for report in reports:
            report2Save = {}
            report2Save["lat"] = report["lat"]
            report2Save["lon"] = report["lon"]
            report2Save["desc"] = report["desc"]
            report2Save['createdAtUTC'] = report['createdAt']
            report2Save['pictures']=[]
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
        reports = db.reports.find({'pictures': ObjectId(imgId)})
        for report in reports:
            report["pictures"] = list(filter(lambda img: not(imgId == str(img)), report["pictures"]))
            db.reports.update_one({'_id':ObjectId(report["_id"])}, {"$set": report}, upsert=False)

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
            pictures.append(ObjectId(doc["_id"]))   
        
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
    
    #the idea to randomly fix reports:
    #take open reports in areas - plot distance to area center / creation time - separate this space through a line,
    #prioritize the lower half (closer to center and further in time then) and create random fix time within a week, the other half within 
    #the following week
    def fixReportsRandomly(self):
        reportMap = {}
    
        reports = self.getLiveReports()

        areas = self.getAreas()
        numReports = len(reports)
        if numReports == 0:
            print("No reports to fix!!")
            exit()
        numContained = 0
        for area in areas:
            areaname = area['areaName']
            pointsPolygon1 = area['points']
            listPoints = []
            reportMap[areaname] = []
            for p in pointsPolygon1:
                listPoints.append(Point(p[0],p[1]))
            polygon = Polygon(listPoints)
            for report in reports:
                point = Point(report['lon'], report['lat'])
                if polygon.contains(point):
                    report['area'] = areaname
                    report['distance2Centroid'] = point.distance(polygon.centroid)
                    reportMap[areaname].append(report)
                    
                    numContained = numContained + 1

        returnMap = {}    
        for areaname in reportMap:
            returnMap[areaname] = {}
            reportsInArea = reportMap[areaname]      
            xs = []
            ys = []
            zs=[]
            for report in reportsInArea:
                xs.append(report["distance2Centroid"])
                ys.append(report["createdAtUTC"])

            xs = np.array(xs)
            ys = np.array(ys)
            xsUp = []
            ysUp = []
            xsDown = []
            ysDown = []

            m,b=self.findSlopeYIntercept(xs.min(), ys.max(), xs.max(), ys.min())
            for i in range(len(xs)):
                x=xs[i]
                y =ys[i]
                yB = x*m + b
                sampleNum = np.random.rand()
                weekStart=0
                weekEnd=1000*60*60*24*7
                #higher = None
                if y >= yB:
                    weekStart=weekEnd
                    weekEnd=weekEnd*2
                    ysUp.append(y)
                    xsUp.append(x)
                    #higher=True
                else:
                    ysDown.append(y)
                    xsDown.append(x) 
                    #higher=False
                fixtime = (weekEnd - weekStart)*sampleNum + weekStart + y
                reportsInArea[i]["fixedAtUTC"] = fixtime
                zs.append(fixtime)
                #diff = fixtime - y
                
            self.bulkFixReport(reportsInArea)
            returnMap[areaname]['xs'] =xs
            returnMap[areaname]['ys'] =ys
            returnMap[areaname]['zs'] =zs
            returnMap[areaname]['xsDown'] =xsDown
            returnMap[areaname]['ysDown'] =ysDown
            returnMap[areaname]['xsUp'] =xsUp
            returnMap[areaname]['ysUp'] =ysUp
        return returnMap    



        


        

        



        