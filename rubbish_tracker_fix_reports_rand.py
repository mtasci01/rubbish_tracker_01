
from service.rubbish_tracker_service import RubbishTrackerService


service = RubbishTrackerService()

reports = service.getAllReports()
print(len(reports))
reports = list(filter(lambda r: not('fixedAtUTC' in r), reports))
print(len(reports))
print(reports[0])