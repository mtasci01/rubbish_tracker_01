
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

imgObj = service.downloadReportImg("664923acddae83fd7dcb6d5d")

rightnowUTC = rightnowUTC = service.getRightnowUTC()

with open(str(rightnowUTC) + "_" + imgObj["filename"], "wb") as binary_file:
    binary_file.write(imgObj["imgBytes"])