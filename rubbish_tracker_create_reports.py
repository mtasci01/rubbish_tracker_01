import datetime
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)

reports = [{
    "lat":35.6,
    "lon":34.8,
    "desc":"rubbish report test " + str(rightnowUTC)
}]

service.createReports(reports, "663237f521069086cf3647ef")

