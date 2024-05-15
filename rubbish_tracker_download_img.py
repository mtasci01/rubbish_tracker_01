
import datetime
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

imgObj = service.downloadReportImg("6636065034fff810067180d3")

rightnowUTC = rightnowUTC = service.getRightnowUTC()

with open(str(rightnowUTC) + "_" + imgObj["filename"], "wb") as binary_file:
    binary_file.write(imgObj["imgBytes"])