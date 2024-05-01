from matplotlib import pyplot as plt
import numpy as np

from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

reports = service.getLiveReports()

points = []
for json in reports:
    point = [json["lon"],json["lat"]]
    points.append(point)
npPoints= np.array(points)
plt.scatter(npPoints[:,0],npPoints[:, 1],color='red')
plt.show()

