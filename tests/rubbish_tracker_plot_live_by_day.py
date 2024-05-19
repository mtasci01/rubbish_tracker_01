from matplotlib import pyplot as plt
import pandas as pd
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()
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