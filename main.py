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
    rightnowUTC = service.getRightnowUTC()
    filename='reports_out_' + str(rightnowUTC) + '.json'
    service.writeFile(filename,reports)
elif val == "2":
    rightnowUTC = service.getRightnowUTC()
    areas = service.getAreas()
    filename='areas_out_' + str(rightnowUTC) + '.json'
    service.writeFile(filename,areas)
else:
    print("Unknown choice. Exiting now")
 