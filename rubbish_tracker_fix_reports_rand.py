import datetime
from time import localtime, strftime
from matplotlib import pyplot as plt
import numpy as np
from shapely.geometry.polygon import Polygon
from service.rubbish_tracker_service import RubbishTrackerService 
from shapely.geometry import Point


service = RubbishTrackerService()

reports = service.getAllReports()

reportMap = {}

reports = list(filter(lambda r: not('fixedAtUTC' in r), reports))
areas = service.getAreas()
numReports = len(reports)
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

def printEpoch(epochMillis):
    return datetime.datetime.fromtimestamp(epochMillis/1000).strftime('%c')      
for areaname in reportMap:
    reportsInArea = reportMap[areaname]      
    xs = []
    ys = []
    zs=[]
    for report in reportsInArea:
        #if str(report['area']).lower()  == "perugia":
        xs.append(report["distance2Centroid"])
        ys.append(report["createdAtUTC"])

    xs = np.array(xs)
    ys = np.array(ys)

    def findSlopeYIntercept(x1,y1,x2,y2):
        m = (y2-y1)/(x2-x1)
        b = y2 - m*x2
        return m,b

    xsUp = []
    ysUp = []

    xsDown = []
    ysDown = []

    m,b=findSlopeYIntercept(xs.min(), ys.max(), xs.max(), ys.min())
    for i in range(len(xs)):
        x=xs[i]
        y =ys[i]
        yB = x*m + b
        sampleNum = np.random.rand()
        weekStart=0
        weekEnd=1000*60*60*24*7
        higher = None
        if y >= yB:
            weekStart=weekEnd
            weekEnd=weekEnd*2
            ysUp.append(y)
            xsUp.append(x)
            higher=True
        else:
            ysDown.append(y)
            xsDown.append(x) 
            higher=False
        fixtime = (weekEnd - weekStart)*sampleNum + weekStart + y
        reportsInArea[i]["fixedAtUTC"] = fixtime
        zs.append(fixtime)
        diff = fixtime - y
        print("y " + printEpoch(y) + " fixtime " + printEpoch(fixtime) + " higher " + str(higher) + " diff " + str(diff))
        

    xsDown = np.array(xsDown)
    ysDown = np.array(ysDown)  

    xsUp = np.array(xsUp)
    ysUp = np.array(ysUp)  
    zs = np.array(zs) 

    #plt.scatter(xsDown,ysDown,color='red')
    #plt.scatter(xsUp,ysUp,color='green')
    #plt.axline((xs.min(), ys.max()), (xs.max(), ys.min()))
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(xs, ys, zs, c=zs, cmap='Greens')
    plt.show()             


