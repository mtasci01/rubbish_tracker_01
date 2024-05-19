import json
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

print("Salvete! This is the RUBBISH TRACKER Menu.")
print("")
print("Choose one of the following:")
print("1. Download reports")
print("2. Download areas")
print("3. Print single report")
print("4. Print single area")
print("5. Download Image")

val = input("Enter your choice: ") 
if val == "1":
    print("Choose: 1. All reports; 2. Live Reports; 3. Fixed Reports")
    val2 = input("Enter your choice: ")
    reports=[]
    if val2 == "1":
        reports = service.getAllReports()
    elif val2 == "2":
        reports = service.getLiveReports()
    elif val2 == "3":
        reports = service.getFixedReports()
    else:
        print("Unknown choice. Exiting now")             
    print("found num reports: " + str(len(reports)))     
    filename='reports_out_' + str(service.getRightnowUTC()) + '.json'
    service.writeFile(filename,reports)
elif val == "2":
    areas = service.getAreas()
    filename='areas_out_' + str(service.getRightnowUTC()) + '.json'
    service.writeFile(filename,areas)
elif val == "3":
    reportId = input("Enter the report id: ")
    report = service.getReport(reportId)
    print("Lat: " + str(report['lat']))
    print("Lon: " + str(report['lon']))
    print("desc: " + str(report['desc']))
    print("pictures: " + str(report['pictures']))
    print("created at utc: " + service.printEpoch(report["createdAtUTC"]))
    if ("fixedAtUTC" in report):
        print("fixed at utc: " + service.printEpoch(report["fixedAtUTC"]))
elif val == "4":
    areaId = input("Enter the area id: ")
    area = service.getArea(areaId)
    print("areaname: " + str(area['areaName']))
    print("points: " + str(area['points']))
    print("saved at utc: " + str(area['savedAtUTC']))
    print("polygon area: " + str(area['polyArea']))
elif val == "5":
    imgId = input("Enter the image id: ")
    imgObj = service.downloadReportImg(imgId)
    theBytes = imgObj["imgBytes"]
    filename = str(service.getRightnowUTC()) + "_" + imgObj["filename"]
    service.writeBinaryFile(filename,theBytes)        
else:
    print("Unknown choice. Exiting now")
 