import json
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from service.rubbish_tracker_service import RubbishTrackerService
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

service = RubbishTrackerService()

print("Salvete! This is the RUBBISH TRACKER Menu.")
print("")
print("Choose one of the following:")
print("1. Download reports")
print("2. Download areas")
print("3. Print single report")
print("4. Print single area")
print("5. Download Image")
print("6. Plot Live Reports")
print("7. Plot Live Reports Day by Day")
print("8. Get Random points in Circle")
print("9. Create Area")
print("10. Create Report")

def downloadReports():
    print("Choose: 1. All reports; 2. Live Reports; 3. Fixed Reports")
    val2 = input("Enter your choice: ")
    reports=[]
    if val2 == "1":
        reports = service.getAllReports()
    elif val2 == "2":
        reports = service.getLiveReports()
    elif val2 == "3":
        reports = service.getFixedReports()
    else:
        print("Unknown choice. Exiting now")             
    print("found num reports: " + str(len(reports)))     
    filename='reports_out_' + str(service.getRightnowUTC()) + '.json'
    service.writeFile(filename,reports)

def downloadAreas():
    areas = service.getAreas()
    filename='areas_out_' + str(service.getRightnowUTC()) + '.json'
    service.writeFile(filename,areas)

def printSingleReport():
    reportId = input("Enter the report id: ")
    report = service.getReport(reportId)
    print("Lat: " + str(report['lat']))
    print("Lon: " + str(report['lon']))
    print("desc: " + str(report['desc']))
    print("pictures: " + str(report['pictures']))
    print("created at utc: " + service.printEpoch(report["createdAtUTC"]))
    if ("fixedAtUTC" in report):
        print("fixed at utc: " + service.printEpoch(report["fixedAtUTC"]))

def printSingleArea():
    areaId = input("Enter the area id: ")
    area = service.getArea(areaId)
    print("areaname: " + str(area['areaName']))
    print("points: " + str(area['points']))
    print("saved at utc: " + str(area['savedAtUTC']))
    print("polygon area: " + str(area['polyArea']))

def downloadImage():
    imgId = input("Enter the image id: ")
    imgObj = service.downloadReportImg(imgId)
    theBytes = imgObj["imgBytes"]
    filename = str(service.getRightnowUTC()) + "_" + imgObj["filename"]
    service.writeBinaryFile(filename,theBytes)

def plotLiveReports():
    points = []
    livereports= service.getLiveReports()
    for json in livereports:
        point = [json["lon"],json["lat"]]
        points.append(point)
    npPoints= np.array(points)
    plt.scatter(npPoints[:,0],npPoints[:, 1],color='red')
    plt.show()

def plotReportsDayByDay():
    l = service.getLiveReportsByDay()
    dataObjList = []

    for o in l:
        year = str(o["_id"]["year"])
        month = str(o["_id"]["month"])
        if len(month) == 1:
            month = "0"+month
        day = str(o["_id"]["day"])
        if len(day) == 1:
            day = "0"+day          
        datestr = year + "-" + month + "-" + day
        dataObj = {"datestr":datestr,"totaldocs":o['totaldocs'],"dateint":int(datestr.replace('-',''))}
        dataObjList.append(dataObj)

    dataObjList.sort(key=lambda x: x['dateint'], reverse=False)    

    date_time_xs = []
    ys = []
    for dataObj in dataObjList:
        date_time_xs.append(dataObj['datestr'])
        ys.append(dataObj['totaldocs'])
    date_time_xs = pd.to_datetime(date_time_xs)

    DF = pd.DataFrame()
    DF['value'] = ys
    DF = DF.set_index(date_time_xs)
    plt.plot(DF)
    plt.gcf().autofmt_xdate()
    plt.show()

def getRandomPointsInCircle():
    centerX = input("Enter the center x: ")
    centerY = input("Enter the center y: ")
    radius = input("Enter the radius: ")
    numPoints = input("Enter the number of points: ")
    points = np.array(service.randomPointsInCircle([float(centerX),float(centerY)], float(radius), int(numPoints)))
    plt.scatter(points[:,0],points[:, 1],color='red')
    plt.show()

def createArea():
    areaname = input("Enter the area name: ")
    pointsStr = input("Enter the points as a 2d array. Remember order matters as the polygon needs to be a closed shape: ")
    points = json.loads(pointsStr)
    service.saveArea(points,areaname,None)

def createReport():
    print("create report todo")

val = input("Enter your choice: ") 
if val == "1":
    downloadReports()
elif val == "2":
    downloadAreas()
elif val == "3":
    printSingleReport()
elif val == "4":
    printSingleArea()
elif val == "5":
    downloadImage()
elif val == "6":
   plotLiveReports()
elif val == "7":
   plotReportsDayByDay()  
elif val == "8":
   getRandomPointsInCircle()
elif val == "9":
   createArea()    
elif val == "10":
   createReport()         
else:
    print("Unknown choice. Exiting now")


 