from matplotlib import pyplot as plt
import pandas as pd
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()
l = service.getLiveReportsByDay()

date_time = []
data = []

for o in l:
    date_time.append(str(o["_id"]["year"]) + "-" + str(o["_id"]["month"]) + "-" + str(o["_id"]["day"]))
    data.append(o['totaldocs'])
date_time = pd.to_datetime(date_time)    

DF = pd.DataFrame()
DF['value'] = data
DF = DF.set_index(date_time)
plt.plot(DF)
plt.gcf().autofmt_xdate()
plt.show()