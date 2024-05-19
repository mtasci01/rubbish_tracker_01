from matplotlib import pyplot as plt
import numpy as np


from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

points = np.array(service.randomPointsInCircle([15,16], 10, 1000))
plt.scatter(points[:,0],points[:, 1],color='red')
plt.show()