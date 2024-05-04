from matplotlib import pyplot as plt
import numpy as np

from shapely.geometry.polygon import Polygon
from service.rubbish_tracker_service import RubbishTrackerService 
from shapely.geometry import Point

service = RubbishTrackerService()

reports = service.getLiveReports()

#the edges must be drawn in sequence
area = service.getArea("6636a276067a84bae086dd20")
pointsPolygon1 = area['points']
listPoints = []
for p in pointsPolygon1:
    listPoints.append(Point(p[0],p[1]))

polygon1 = Polygon(listPoints)
result = service.countReportsInPolygon(polygon1, reports)
print("polygon1 tot " + str(result['tot']) + " - contained " + str(result['contained']))

polygon2 = Polygon([(110., 140.), (110., 150.), (115., 150.), (115., 140.)])
result = service.countReportsInPolygon(polygon2, reports)
print("polygon2 tot " + str(result['tot']) + " - contained " + str(result['contained']))


npPolygon1= np.array(pointsPolygon1)
plt.scatter(npPolygon1[:,0],npPolygon1[:, 1],color='blue')
points = []
for report in reports:
    points.append([report['lon'], report['lat']])
npPoints= np.array(points)
plt.scatter(npPoints[:,0],npPoints[:, 1],color='red')
plt.show()








 