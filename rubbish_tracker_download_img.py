
import datetime
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

imgObj = service.downloadReportImg("663265b6976f3ac40985ad2e")

rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)

with open(str(rightnowUTC) + "_" + imgObj["filename"], "wb") as binary_file:
    binary_file.write(imgObj["imgBytes"])