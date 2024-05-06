import datetime
import numpy as np
from shapely.geometry import Polygon

from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()
romeAreaId = "6636a57efc30c3d68543acfe"
perugiaAreaId = "66393d57632adb082d8f0b2b"
userId = "663237f521069086cf3647ef"
area = service.getArea(perugiaAreaId)

polygon = Polygon(area['points'])
points = service.randomPointsinPolygon(polygon, 100)


reports2Save = []
i = 0
rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp())
oneMonthAgo =  rightnowUTC - 60*60*24*30
for point in points:
    createTime = np.random.randint(oneMonthAgo,rightnowUTC)*1000
    reqJsonO = {"lat":point[1], "lon":point[0],"createdAt":createTime, "desc":"rubbish report " + str(createTime) + "_" + str(i)}
    reports2Save.append(reqJsonO)
    i = i + 1
result = service.countReportsInPolygon(polygon, reports2Save)    
print(result)
service.createReports(reports2Save, userId)

