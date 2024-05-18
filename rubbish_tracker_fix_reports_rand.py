from matplotlib import pyplot as plt
import numpy as np
from shapely.geometry.polygon import Polygon
from service.rubbish_tracker_service import RubbishTrackerService 
from shapely.geometry import Point


service = RubbishTrackerService()

reports = service.getAllReports()

reports = list(filter(lambda r: not('fixedAtUTC' in r), reports))
areas = service.getAreas()
numReports = len(reports)
numContained = 0
for area in areas:
    pointsPolygon1 = area['points']
    listPoints = []
    for p in pointsPolygon1:
        listPoints.append(Point(p[0],p[1]))
    polygon = Polygon(listPoints)
    for report in reports:
        point = Point(report['lon'], report['lat'])
        if polygon.contains(point):
            report['area'] = area['areaName']
            report['distance2Centroid'] = point.distance(polygon.centroid)
            
            numContained = numContained + 1
xs = []
ys = []
for report in reports:
    if str(report['area']).lower()  == "perugia":
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
    if y >= yB:
        ysUp.append(y)
        xsUp.append(x)
    else:
        ysDown.append(y)
        xsDown.append(x)  

xsDown = np.array(xsDown)
ysDown = np.array(ysDown)  

xsUp = np.array(xsUp)
ysUp = np.array(ysUp)   

plt.scatter(xsDown,ysDown,color='red')
plt.scatter(xsUp,ysUp,color='green')
plt.axline((xs.min(), ys.max()), (xs.max(), ys.min()))
plt.show()             


