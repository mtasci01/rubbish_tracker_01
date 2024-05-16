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
x = []
y = []
for report in reports:
    if str(report['area']).lower()  == "perugia":
        x.append(report["distance2Centroid"])
        y.append(report["createdAtUTC"])

x = np.array(x)
y = np.array(y)
plt.scatter(x,y,color='red')
plt.show()             


