import datetime
from matplotlib import pyplot as plt
import numpy as np
from shapely.geometry.polygon import Polygon
from service.rubbish_tracker_service import RubbishTrackerService 
from shapely.geometry import Point

#the idea to randomly fix reports:
#take open reports in areas - plot distance to area center / creation time - separate this space through a line,
#prioritize the lower half (closer to center and further in time then) and create random fix time within a week, the other half within 
#the following week

service = RubbishTrackerService()

reports = service.getAllReports()



def printEpoch(epochMillis):
    return datetime.datetime.fromtimestamp(epochMillis/1000).strftime('%c')

def findSlopeYIntercept(x1,y1,x2,y2):
    m = (y2-y1)/(x2-x1)
    b = y2 - m*x2
    return m,b

reportMap = {}

reports = list(filter(lambda r: not('fixedAtUTC' in r) or r['fixedAtUTC'] == None, reports))
areas = service.getAreas()
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

      
for areaname in reportMap:
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
        
    service.bulkFixReport(reportsInArea)

    xsDown = np.array(xsDown)
    ysDown = np.array(ysDown)  

    xsUp = np.array(xsUp)
    ysUp = np.array(ysUp)  
    zs = np.array(zs) 
    plt.xlabel("distance to area center")
    plt.ylabel("creation time")
    plt.title(areaname)
    plt.scatter(xsDown,ysDown,color='red')
    plt.scatter(xsUp,ysUp,color='green')
    plt.axline((xs.min(), ys.max()), (xs.max(), ys.min()))

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.set_title(areaname)
    ax.set_xlabel('distance to area center')
    ax.set_ylabel('creation time')
    ax.set_zlabel('fix time')
    ax.scatter3D(xs, ys, zs, c=zs, cmap='Greens')
    plt.show()             


